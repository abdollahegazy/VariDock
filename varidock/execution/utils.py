import subprocess

def run_with_interrupt(argv, **kwargs):
    process = subprocess.Popen(argv, **kwargs)  # start the process
    try:
        process.wait()  # block until it finishes
    except KeyboardInterrupt:  # user hit Ctrl+C
        process.terminate()  # send SIGTERM to the subprocess
        try:
            process.wait(timeout=5)  # wait up to 5 seconds
        except subprocess.TimeoutExpired:
            process.kill()           # force kill if still alive
            process.wait()
        raise  # re-raise the KeyboardInterrupt so Python exits

    if process.returncode != 0:  # process failed
        raise subprocess.CalledProcessError(process.returncode, argv)
