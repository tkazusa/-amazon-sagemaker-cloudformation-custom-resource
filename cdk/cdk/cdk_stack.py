from aws_cdk import (
    core,
    aws_iam,
    aws_sagemaker
)


class SageMakerNotebookStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ====================================
        # IAM Role
        # https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-resource-iam-role.html
        # ====================================
        
        # SageMaker notebook 用のロール
        notebook_role = aws_iam.Role(
            self,
            id = "sagmaker-notebook-role",
            assumed_by = aws_iam.ServicePrincipal('sagemaker.amazonaws.com'),
            role_name  = "sagemaker-notebook-execution-role-cfn"
        )

        sagemaker_fullaccess = aws_iam.ManagedPolicy.from_managed_policy_arn(
            self,
            id = 'sagemaker-fullaccess-managedpolicy',
            managed_policy_arn = 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess')

        stepfunctions_fullaccess = aws_iam.ManagedPolicy.from_managed_policy_arn(
            self,
            id =  'stepfunctions-fullaccess-managedpolicy',
            managed_policy_arn = 'aarn:aws:iam::aws:policy/AWSStepFunctionsFullAccess' 
        )

        sm_execution_policy = aws_iam.ManagedPolicy(
            self,
            id = "sagemaker-execution-policy",
            managed_policy_name = 'AmazonSageMaker-ExecutionPolicy-cfn'
        )

        sm_policy_statement = aws_iam.PolicyStatement()
        sm_policy_statement.add_actions("s3:GetObject")
        sm_policy_statement.add_actions("s3:PutObject")
        sm_policy_statement.add_actions("s3:DeleteObject")
        sm_policy_statement.add_actions("s3:ListBucket")
        sm_policy_statement.add_resources(
            "arn:aws:s3:::*"
            )

        sm_execution_policy.add_statements(sm_policy_statement)

        notebook_role.add_managed_policy(sagemaker_fullaccess)
        notebook_role.add_managed_policy(stepfunctions_fullaccess)
        notebook_role.add_managed_policy(sm_policy_statement)


        # StepFunctions の実行ロール 
        sfn_execution_role = aws_iam.Role(
            self,
            id = 'StepFunctionsWorkflowExecutionRole',
            assumed_by = aws_iam.ServicePrincipal('states .amazonaws.com'),
            role_name  = "StepFunctionsWorkflowExecutionRole-cfn"
        )      
        
        sfn_policy_statement_steps = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions= [
                "sagemaker:CreateTransformJob",
                "sagemaker:DescribeTransformJob",
                "sagemaker:StopTransformJob",
                "sagemaker:CreateTrainingJob",
                "sagemaker:DescribeTrainingJob",
                "sagemaker:StopTrainingJob",
                "sagemaker:CreateHyperParameterTuningJob",
                "sagemaker:DescribeHyperParameterTuningJob",
                "sagemaker:StopHyperParameterTuningJob",
                "sagemaker:CreateModel",
                "sagemaker:CreateEndpointConfig",
                "sagemaker:CreateEndpoint",
                "sagemaker:DeleteEndpointConfig",
                "sagemaker:DeleteEndpoint",
                "sagemaker:UpdateEndpoint",
                "sagemaker:ListTags",
                "lambda:InvokeFunction",
                "sqs:SendMessage",
                "sns:Publish",
                "ecs:RunTask",
                "ecs:StopTask",
                "ecs:DescribeTasks",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "batch:SubmitJob",
                "batch:DescribeJobs",
                "batch:TerminateJob",
                "glue:StartJobRun",
                "glue:GetJobRun",
                "glue:GetJobRuns",
                "glue:BatchStopJobRun"
            ],
            resources=['*']
        )

        sfn_policy_statement_passrole = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["iam:PassRole"],
            resources=["*"],
            conditions={"StringEquals": {
                    "iam:PassedToService": "sagemaker.amazonaws.com"}}  
        )

        sfn_policy_statement_events = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=[
                "events:PutTargets",
                "events:PutRule",
                "events:DescribeRule"     
            ],
            resources=[
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTrainingJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTransformJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForSageMakerTuningJobsRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForECSTaskRule",
                "arn:aws:events:*:*:rule/StepFunctionsGetEventsForBatchJobsRule"
            ]
        )

        sfn_policy = aws_iam.Policy(
            self,
            id = "stepfunctions-execution-policy",
            statements=[
                sfn_policy_statement_steps,
                sfn_policy_statement_passrole,
                sfn_policy_statement_events
            ]
        )

        sfn_execution_role.attach_inline_policy(sfn_policy)


        # ====================================
        # Amazn SageMaker notebook instance
        # ====================================
        notebook_instance = aws_sagemaker.CfnNotebookInstance(
            self,
            id = "sagemaker-notebook",
            instance_type= 'ml.t2.medium',
            role_arn =notebook_role.role_arn
        )
