# How to extend AI Flow

## Key Concepts

1. job: The basic unit that can be executed.It can run on different platforms.
2. job config: Job configuration information, including job name, running environment, etc.
3. platform: The running environment of the job, such as local, kubernetes, yarn, etc.
4. engine: The type of job, such as pytho, cmd_line, flink, etc.
5. job plugin: The job plugin function is to run a job based on a specific platform and engine.
6. job handler: After the scheduler submits the job, it gets the object representing the running job

## Extend platform
Inherit the platform abstract class:

```python
class AbstractPlatform(Jsonable):
    """
    ai flow job must run on one platform, such as local k8s etc.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def platform() -> Text:
        """
        :return platform name:
        """
        raise NotImplementedError("not implement platform")
```
Then call register_platform function to register the platform.
```python
def register_platform(platform: type(AbstractPlatform)):
    pass

```

## Extend engine

Inherit the Engine abstract class:

```python
class AbstractEngine(Jsonable):
    """
    ai flow job must run by one engine, such as python bash etc.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def engine() -> Text:
        """
        :return platform name:
        """
        raise NotImplementedError("not implement engine")

```

## Extend job

Inherit the Job abstract class:

```python
class BaseJob(BaseNode):
    """
    A BaseJob contains the common information of a ai flow job. Users can implement custom jobs by adding other
    execution information for a specific engine and platform.
    """
    def __init__(self, job_context: JobContext, job_config: BaseJobConfig) -> None:
        """

        :param job_context: Job runtime context 
        :param job_config: Job configuration information, including job name, running environment, etc.
        """
```
**alias: AbstractJob**

## Extend job config
Inherit the job config abstract class:

```python
class BaseJobConfig(Jsonable):
    """
    Base class for job config. It is used to set the basic job config.

    """
    def __init__(self, platform: Text = None, engine: Text = None, job_name: Text = None,
                 periodic_config: PeriodicConfig = None, exec_mode: Optional[ExecutionMode] = ExecutionMode.BATCH,
                 properties: Dict[Text, Jsonable] = None) -> None:
        """
        Set platform and engine in base job config.

        :param platform: Platform of the configured job. It can be local or kubernetes.
        :param engine: Engine of the configured job. It can be python, cmd_line flink or other available engine.
        :param job_name: Name of the configured job.
        :param properties: Properties of the configured job.
        """
```
**alias: AbstractJobConfig**

## Extend job plugin
Inherit the job plugin abstract class and implement the abstract method:
```python
class AbstractJobPlugin(AbstractJobGenerator, AbstractJobSubmitter):

    def __init__(self) -> None:
        super().__init__()

    # job generator interface
    @abstractmethod
    def generate(self, sub_graph: AISubGraph, project_desc: ProjectDesc) -> AbstractJob:
        """
        Generate the job to execute.
        :param sub_graph: The subgraph of AI graph, which describes the operation logic of a job
        :param project_desc: The ai flow project description.
        :return: the job.
        """
        pass

    @abstractmethod
    def generate_job_resource(self, job: AbstractJob) -> None:
        pass

    # job submitter interface
    @abstractmethod
    def submit_job(self, job: AbstractJob) -> AbstractJobHandler:
        """
        submit an executable job to run.

        :param job: A base job object that contains the necessary information for an execution.
        :return base_job_handler: a job handler that maintain the handler of a jobs runtime.
        """
        pass

    @abstractmethod
    def stop_job(self, job: AbstractJob):
        """
        Stop a ai flow job.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass

    @abstractmethod
    def cleanup_job(self, job: AbstractJob):
        """
        clean up temporary resources created during this execution.
        :param job: A base job object that contains the necessary information for an execution.
        """
        pass

    # job type
    @abstractmethod
    def job_type(self) -> type(AbstractJob):
        """
        :return: The job type, which is a subclass of AbstractJob type.
        """
        pass

    # job config type
    @abstractmethod
    def job_config_type(self) -> type(AbstractJobConfig):
        """
        :return: The job config type, which is a subclass of AbstractJobConfig type.
        """
        pass

    @abstractmethod
    def platform(self) -> type(AbstractPlatform):
        """
        :return: The platform type, which is a subclass of AbstractPlatform type.
        """
        pass

    @abstractmethod
    def engine(self) -> type(AbstractEngine):
        """
        :return: The engine type, which is a subclass of AbstractEngine type.
        """
        pass
```

At last call register_platform function to register the job plugin.
```python
def register_job_plugin(plugin: AbstractJobPlugin):
    pass

```





