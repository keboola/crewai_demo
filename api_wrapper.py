from datetime import datetime
import importlib.util
import logging
import os
import sys
import uuid
import threading
import json
import requests
from typing import Dict, Any, Optional

import tomli
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Set a longer timeout for the app to handle long-running operations
app = FastAPI(
    title="Content Orchestrator",
    # Note: When running with uvicorn, use the following command line options:
    # --timeout-keep-alive 300 --timeout-notify 300 --timeout-graceful-shutdown 300
)

# Add CORS middleware with security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, specify your actual domains
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# In-memory storage for jobs
jobs = {}

# Load secrets from .streamlit/secrets.toml
try:
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomli.load(f)
        for key, value in secrets.items():
            if isinstance(value, str):
                os.environ[key] = value
        logger.info("Successfully loaded secrets from .streamlit/secrets.toml")
except Exception as e:
    logger.warning(f"Could not load secrets: {e}")

# Import the user's script
script_path = os.getenv("DATA_APP_ENTRYPOINT", "user_script.py")
try:
    spec = importlib.util.spec_from_file_location("user_script", script_path)
    user_module = importlib.util.module_from_spec(spec)
    sys.modules["user_script"] = user_module
    spec.loader.exec_module(user_module)
    logger.info(f"Successfully loaded user script from {script_path}")
except Exception as e:
    logger.error(f"Failed to load user script: {e}")
    raise


def process_job_in_background(
    job_id: str,
    function_name: str,
    args: list,
    kwargs: dict,
    webhook_url: Optional[str] = None,
):
    """
    Process a job in the background and update its status
    """
    try:
        logger.info(f"Starting background job {job_id} for function {function_name}")

        # Update job status to processing
        jobs[job_id]["status"] = "processing"

        # Get the function from the user module
        func = getattr(user_module, function_name)

        # Execute the function
        result = func(*args, **kwargs)

        # Check if the result indicates human approval is needed
        if isinstance(result, dict) and result.get("status") == "needs_approval":
            # Update job status to waiting for human input
            jobs[job_id] = {
                **jobs[job_id],
                "status": "pending_approval",
                "result": result,
                "retry_function": function_name,  # Store function for retry
                "retry_args": args,
                "retry_kwargs": kwargs,
            }
            
            logger.info(f"Job {job_id} waiting for human approval")
            
            # Send webhook notification if URL is provided
            if webhook_url:
                try:
                    webhook_payload = {
                        "job_id": job_id,
                        "status": "pending_approval",
                        "function": function_name,
                        "result": result,
                    }

                    requests.post(
                        webhook_url,
                        json=webhook_payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )
                    logger.info(f"Webhook notification sent for job {job_id} pending approval")
                except Exception as webhook_error:
                    logger.error(
                        f"Failed to send webhook notification for job {job_id}: {str(webhook_error)}"
                    )
        else:
            # Update job with success result
            jobs[job_id] = {
                **jobs[job_id],
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result,
            }

            logger.info(f"Job {job_id} completed successfully")

            # Send webhook notification if URL is provided
            if webhook_url:
                try:
                    webhook_payload = {
                        "job_id": job_id,
                        "status": "completed",
                        "function": function_name,
                        "completed_at": jobs[job_id]["completed_at"],
                        "result": result,
                    }

                    requests.post(
                        webhook_url,
                        json=webhook_payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )
                    logger.info(f"Webhook notification sent for job {job_id}")
                except Exception as webhook_error:
                    logger.error(
                        f"Failed to send webhook notification for job {job_id}: {str(webhook_error)}"
                    )

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")

        # Update job with error information
        jobs[job_id] = {
            **jobs[job_id],
            "status": "error",
            "error_at": datetime.now().isoformat(),
            "error": str(e),
            "error_type": e.__class__.__name__,
        }

        # Send webhook notification about error if URL is provided
        if webhook_url:
            try:
                webhook_payload = {
                    "job_id": job_id,
                    "status": "error",
                    "function": function_name,
                    "error_at": jobs[job_id]["error_at"],
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                }

                requests.post(
                    webhook_url,
                    json=webhook_payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                logger.info(f"Error webhook notification sent for job {job_id}")
            except Exception as webhook_error:
                logger.error(
                    f"Failed to send error webhook notification for job {job_id}: {str(webhook_error)}"
                )


@app.get("/")
async def root():
    """Root endpoint with application status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for the proxy"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "module_loaded": user_module is not None,
        "active_jobs": len([j for j in jobs.values() if j["status"] == "processing"]),
    }


@app.post("/invoke")
async def invoke_function(request: Request, background_tasks: BackgroundTasks):
    """
    Invoke a function asynchronously and return a job ID
    """
    try:
        data = await request.json()
        function_name = data.get("function")
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        webhook_url = data.get("webhook_url")
        wait = data.get("wait", False)  # Option to wait for completion

        if not hasattr(user_module, function_name):
            return JSONResponse(
                status_code=404,
                content={"error": f"Function {function_name} not found"},
            )

        # Generate a unique job ID
        job_id = str(uuid.uuid4())

        # Initialize job in the jobs dictionary
        jobs[job_id] = {
            "id": job_id,
            "function": function_name,
            "args": args,
            "kwargs": kwargs,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "webhook_url": webhook_url,
        }

        logger.info(f"Created job {job_id} for function {function_name}")

        if wait:
            # Synchronous execution - wait for result
            try:
                func = getattr(user_module, function_name)
                result = func(*args, **kwargs)

                # Update job with success result
                jobs[job_id] = {
                    **jobs[job_id],
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "result": result,
                }

                return {"job_id": job_id, "status": "completed", "result": result}
            except Exception as e:
                # Update job with error information
                jobs[job_id] = {
                    **jobs[job_id],
                    "status": "error",
                    "error_at": datetime.now().isoformat(),
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                }

                return JSONResponse(
                    status_code=500,
                    content={"job_id": job_id, "status": "error", "error": str(e)},
                )
        else:
            # Asynchronous execution - start in background
            background_tasks.add_task(
                process_job_in_background,
                job_id,
                function_name,
                args,
                kwargs,
                webhook_url,
            )

            return {
                "job_id": job_id,
                "status": "queued",
                "message": "Function execution started in the background",
            }

    except Exception as e:
        logger.error(f"Error setting up function invocation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/job/{job_id}")
async def get_job(job_id: str):
    """Get the status and result of a specific job"""
    if job_id not in jobs:
        return JSONResponse(
            status_code=404, content={"error": f"Job with ID {job_id} not found"}
        )

    return jobs[job_id]


@app.post("/job/{job_id}/feedback")
async def provide_feedback(
    job_id: str, request: Request, background_tasks: BackgroundTasks
):
    """
    Provide human feedback for a job and optionally resume processing
    """
    if job_id not in jobs:
        return JSONResponse(
            status_code=404, content={"error": f"Job with ID {job_id} not found"}
        )

    # Check if job is in a state that can accept feedback
    if jobs[job_id].get("status") != "pending_approval":
        return JSONResponse(
            status_code=400, 
            content={"error": f"Job {job_id} is not in a state that can accept feedback. Current status: {jobs[job_id].get('status')}"}
        )

    try:
        data = await request.json()
        feedback = data.get("feedback", "")
        approved = data.get("approved", False)

        # Update job with feedback
        jobs[job_id]["feedback"] = feedback
        jobs[job_id]["human_approved"] = approved
        jobs[job_id]["feedback_at"] = datetime.now().isoformat()

        # Get the webhook URL if it exists
        webhook_url = jobs[job_id].get("webhook_url")

        if approved:
            # If approved, mark as completed
            jobs[job_id]["status"] = "completed"
            
            # Send webhook notification if URL is provided
            if webhook_url:
                try:
                    webhook_payload = {
                        "job_id": job_id,
                        "status": "completed",
                        "feedback": feedback,
                        "approved": True,
                        "completed_at": datetime.now().isoformat(),
                    }

                    requests.post(
                        webhook_url,
                        json=webhook_payload,
                        headers={"Content-Type": "application/json"},
                        timeout=10,
                    )
                    logger.info(f"Approval webhook notification sent for job {job_id}")
                except Exception as webhook_error:
                    logger.error(
                        f"Failed to send approval webhook notification for job {job_id}: {str(webhook_error)}"
                    )
                    
            return {
                "message": "Feedback recorded and job marked as completed",
                "job_id": job_id,
            }
        else:
            # If not approved, restart the job with feedback
            # Get the original function and arguments
            retry_function = jobs[job_id].get("retry_function")
            retry_args = jobs[job_id].get("retry_args", [])
            retry_kwargs = jobs[job_id].get("retry_kwargs", {}).copy()  # Make a copy to avoid modifying the original
            
            # Special handling for create_content_with_hitl
            if retry_function == "create_content_with_hitl":
                # Add feedback to kwargs
                retry_kwargs["feedback"] = feedback
                
                # Update job status to processing again
                jobs[job_id]["status"] = "processing"
                
                # Start retry in background
                background_tasks.add_task(
                    process_job_in_background,
                    job_id,
                    retry_function,
                    retry_args,
                    retry_kwargs,
                    webhook_url,
                )
                
                return {
                    "message": "Feedback recorded and content generation restarted with feedback",
                    "job_id": job_id,
                }
            else:
                # No specific HITL handling for this function
                jobs[job_id]["status"] = "rejected"
                
                # Send webhook notification if URL is provided
                if webhook_url:
                    try:
                        webhook_payload = {
                            "job_id": job_id,
                            "status": "rejected",
                            "feedback": feedback,
                            "approved": False,
                            "rejected_at": datetime.now().isoformat(),
                        }

                        requests.post(
                            webhook_url,
                            json=webhook_payload,
                            headers={"Content-Type": "application/json"},
                            timeout=10,
                        )
                        logger.info(f"Rejection webhook notification sent for job {job_id}")
                    except Exception as webhook_error:
                        logger.error(
                            f"Failed to send rejection webhook notification for job {job_id}: {str(webhook_error)}"
                        )
                
                return {
                    "message": "Feedback recorded and job marked as rejected",
                    "job_id": job_id,
                }

    except Exception as e:
        logger.error(f"Error processing feedback for job {job_id}: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/jobs")
async def list_jobs(limit: int = 10, status: Optional[str] = None):
    """List all jobs with optional filtering"""
    filtered_jobs = []

    for job_id, job_data in jobs.items():
        if status is None or job_data.get("status") == status:
            # Create a copy without potentially large result data
            job_summary = {
                "id": job_id,
                "function": job_data.get("function"),
                "status": job_data.get("status"),
                "created_at": job_data.get("created_at"),
                "completed_at": job_data.get("completed_at", None),
                "has_result": "result" in job_data,
                "has_error": "error" in job_data,
            }
            filtered_jobs.append(job_summary)

    # Sort by created_at (newest first)
    filtered_jobs.sort(key=lambda x: x["created_at"], reverse=True)

    # Apply limit
    filtered_jobs = filtered_jobs[:limit]

    return {"jobs": filtered_jobs, "count": len(filtered_jobs), "total_jobs": len(jobs)}


@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from the jobs dictionary"""
    if job_id not in jobs:
        return JSONResponse(
            status_code=404, content={"error": f"Job with ID {job_id} not found"}
        )

    del jobs[job_id]
    return {"message": f"Job {job_id} deleted successfully"}


@app.get("/list-functions")
async def list_functions():
    """List available functions in the user module"""
    try:
        functions = [
            name
            for name, obj in vars(user_module).items()
            if callable(obj) and not name.startswith("_")
        ]
        return {"functions": functions}
    except Exception as e:
        logger.error(f"Error listing functions: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})
