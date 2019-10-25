from abc import abstractmethod


class AbstractProjectRun(object):
    """
    Wrapper around an MLflow project run (e.g. a subprocess running an entry point
    command or a Databricks job run) and exposing methods for waiting on and cancelling the run.
    This class defines the interface that the MLflow project runner uses to manage the lifecycle
    of runs launched in different environments (e.g. runs launched locally or on Databricks).

    ``SubmittedRun`` is not thread-safe. That is, concurrent calls to wait() / cancel()
    from multiple threads may inadvertently kill resources (e.g. local processes) unrelated to the
    run.

    NOTE:

        Subclasses of ``SubmittedRun`` must expose a ``run_id`` member containing the
        run's MLflow run ID.
    """

    @abstractmethod
    def wait(self):
        """
        Wait for the run to finish, returning True if the run succeeded and false otherwise. Note
        that in some cases (e.g. remote execution on Databricks), we may wait until the remote job
        completes rather than until the MLflow run completes.
        """
        pass

    @abstractmethod
    def get_status(self):
        """
        Get status of the run.
        """
        pass

    @abstractmethod
    def cancel(self):
        """
        Cancel the run (interrupts the command subprocess, cancels the Databricks run, etc) and
        waits for it to terminate. The MLflow run status may not be set correctly
        upon run cancellation.
        """
        pass

    @property
    @abstractmethod
    def run_id(self):
        pass

    @abstractmethod
    def submit_run(self):
        pass
