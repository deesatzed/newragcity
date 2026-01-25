# Regulus Backend Integration: Status Report and Handoff

**Date:** 2025-08-30

## 1. Objective

The primary goal is to replace the dummy modules in the Regulus backend with real components to enable PDF document indexing and querying. This involves integrating the `leann` and `pageindex` libraries, fixing module import and initialization errors, and ensuring the backend container runs successfully with live code reloading.

## 2. Summary of Progress

We have made significant progress in transitioning the backend from a placeholder implementation to a functional service:

*   **Real PDF Processing**: Implemented `process_pdf` in `app/indexing.py` using `PyMuPDF` to extract text from uploaded PDF files, replacing the non-existent `page_index_main`.
*   **Leann Integration**: Replaced the dummy `LeannBuilder` and `Searcher` with the real `LeannBuilder` and `LeannSearcher` from the `leann-core` library.
*   **Dependency Management**: Added `PyMuPDF` to `pyproject.toml` and removed the local dummy `pageindex` directory from the Docker build to ensure the correct libraries are used.
*   **Docker Configuration**: Iteratively debugged and refined the Docker setup to handle dependency installation, environment variables, and live-reloading.

## 3. Debugging Journey & Key Fixes

We addressed several critical issues to get the backend to its current state:

1.  **`TypeError` on `LeannBuilder`**: Fixed by providing the required `backend_name="hnsw"` argument during initialization in `app/indexing.py`.
2.  **`ValueError: Backend 'hnsw' not found`**: This error persisted despite calling `autodiscover_backends()`. The root cause was that project dependencies were not installed in the running container.
3.  **Missing Dependencies in Container**: We discovered that the volume mount `./backend:/app` in `docker-compose.yml` was overwriting the `venv` where dependencies were installed during the image build.
4.  **Docker Environment Isolation**: To fix this, we modified the `Dockerfile` to create the virtual environment in `/opt/venv`, outside the application directory. This prevents the volume mount from interfering with installed packages.
5.  **Startup Script Failures**: After isolating the venv, the container failed to start because the `uvicorn` command could not be found. This was traced to two issues:
    *   The `uv run` command in `docker-compose.yml` created a temporary, isolated environment without the necessary dependencies.
    *   The `wait-for-postgres.sh` script's shell (`/bin/sh`) did not have the updated `PATH` to locate the `uvicorn` executable in `/opt/venv/bin`.
6.  **Final Startup Fix**: We resolved this by hardcoding the full path to the `uvicorn` executable (`/opt/venv/bin/uvicorn`) directly into the `wait-for-postgres.sh` script and simplifying the `command` in `docker-compose.yml`.

## 4. Current Blocker: Silent Container Failure

After the last fix, the `backend` container fails to start. Both `docker-compose logs backend` and `docker-compose ps` return empty output, which indicates the container is exiting immediately upon launch, before the logging service can attach.

This type of silent failure is often caused by an issue in the entrypoint script (`wait-for-postgres.sh`) or a fundamental problem with the container's command or environment that prevents the main process from even starting.

## 5. Next Steps for Resumption

When you return, the immediate priority is to diagnose why the `backend` container is failing silently.

1.  **Inspect Exited Containers**: Run `docker-compose ps -a` to view the status of all containers, including those that have exited. This will confirm if the `backend` container is exiting and provide an exit code.

2.  **Check Container Logs Directly**: If `docker-compose logs` is not working, you can try to get logs from the container ID directly (retrieved from `docker-compose ps -a`):
    ```bash
    docker logs <container_id>
    ```

3.  **Simplify the Entrypoint**: Temporarily modify the `command` in `docker-compose.yml` to something simple like `tail -f /dev/null`. This will keep the container running and allow you to `exec` into it to manually run scripts and check the environment, paths, and file permissions.
    ```bash
    # In docker-compose.yml
    command: ["tail", "-f", "/dev/null"]
    ```
    Then, exec into the container:
    ```bash
    docker-compose exec backend /bin/sh
    # Inside the container, manually run the script
    ./wait-for-postgres.sh postgres
    ```

4.  **Verify Script and Executable**: Once inside the container, verify that `/opt/venv/bin/uvicorn` exists and is executable.

Once the container starts successfully, the final steps will be to test the end-to-end functionality:

*   **Upload a PDF**: `curl -X POST -F 'file=@/Volumes/WS4TB/ERSATZ_RAG/WS_ED/ECEDHandbook_Latest.pdf' http://localhost:8000/upload`
*   **Query the Index**: `curl -X POST -F 'query=handbook' http://localhost:8000/query`

This document provides a complete snapshot of our progress and a clear path forward. Please let me know if you have any questions before you sign off.
