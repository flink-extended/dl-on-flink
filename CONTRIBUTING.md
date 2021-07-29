# Contributing guidelines

## Pull Request Checklist

Before sending your pull requests, make sure you followed this list.

- Read [contributing guidelines](CONTRIBUTING.md).
- Open an issue (https://github.com/alibaba/flink-ai-extended/issues)
- Create a personal fork of the project on Github.
- Clone the fork on your local machine. Your remote repo on Github is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.
- Create a new branch to work on! Branch from `master`.
- Implement/fix your feature, comment your code.
- Follow the code style of the project, including indentation.

   [java example](flink-ml-framework/src/main/java/com/alibaba/flink/ml/cluster/MLConfig.java)
   
   [python example](flink-ml-framework/python/flink_ml_framework/context.py)
   
   [c++ example](flink-ml-framework/python/flink_ml_framework/ops/java_file_python_binding.cc)
- Run tests.
- Write or adapt tests as needed.
- Add or change the documentation as needed.
- Create a new branch.
- Push your branch to your fork on Github, the remote `origin`.
- From your fork open a pull request in the correct branch. Go for `master`!
- Wait for approval.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete your extra branches.

## Development Notices for AI Flow

Currently the AI Flow project is under the `flink-ai-flow` directory. 
If you are contributing to AI Flow, it is recommended to change your working directory to `flink-ai-flow`.
The paths mentioned in following content are all relative paths based on `flink-ai-flow`.

### Prerequisites
1. java
2. maven

### Establish Development Environment

We strongly recommend using [virtualenv](https://virtualenv.pypa.io/en/latest/index.html) or other similar tools for an isolated Python environment in case of dependencies conflict error, e.g.

```shell
python3 -m venv /path/to/new/virtual/environment
source /path/to/new/virtual/environment/bin/activate
```

Now you can configure it as the Project Interpreter if you are using PyCharm as your IDE.

### Run Tests

You can run the shell script `run_tests.sh` to verify the modification of AI Flow. 

If you modified the bundled Airflow, you need to add relevant test cases and run tests according to [Airflow contributing guidelines](flink-ai-flow/lib/airflow/CONTRIBUTING.rst).

If you modified the bundled Notification Services, you need to add relevant test cases to `lib/notification_service/tests/test_notification.py` and run the test script.

### Contact Us

For more information, you can join the **Flink AI Flow Users Group** on [DingTalk](https://www.dingtalk.com) to contact us.
The number of the DingTalk group is `35876083`. 

You can also join the group by scanning the QR code below:

![](flink-ai-flow/doc/images/dingtalk_qr_code.png)
