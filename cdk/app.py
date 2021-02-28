#!/usr/bin/env python3

from aws_cdk import core

from cdk.cdk_stack import SageMakerNotebookStack


app = core.App()
SageMakerNotebookStack(app, "SageMakerNotebook")

app.synth()
