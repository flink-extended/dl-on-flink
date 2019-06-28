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