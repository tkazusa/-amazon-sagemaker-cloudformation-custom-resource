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
        sagemaker_fullaccess = aws_iam.ManagedPolicy.from_managed_policy_arn(
            self,
            id = 'sagemaker-fullaccess-managedpolicy',
            managed_policy_arn = 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess')
        
        execution_policy = aws_iam.ManagedPolicy(
            self,
            id = "sagemaker-execution-policy",
            managed_policy_name = 'AmazonSageMaker-ExecutionPolicy-cfn'
        )

        # ポリシー作成
        policy_statement = aws_iam.PolicyStatement()
        policy_statement.add_actions("s3:GetObject")
        policy_statement.add_actions("s3:PutObject")
        policy_statement.add_actions("s3:DeleteObject")
        policy_statement.add_actions("s3:ListBucket")
        policy_statement.add_resources(
            "arn:aws:s3:::*"
            )

        execution_policy.add_statements(policy_statement)

        notebook_role = aws_iam.Role(
            self,
            id = "sagmaker-notebook-role",
            assumed_by = aws_iam.ServicePrincipal('sagemaker.amazonaws.com'),
            role_name  = "sagemaker-notebook-execution-role-cfn"
        )
        notebook_role.add_managed_policy(sagemaker_fullaccess)
        notebook_role.add_managed_policy(execution_policy)

        # ====================================
        # Amazn SageMaker notebook instance
        # ====================================
        notebook_instance = aws_sagemaker.CfnNotebookInstance(
            self,
            id = "sagemaker-notebook",
            instance_type= 'ml.t2.medium',
            role_arn =notebook_role.role_arn
        )


