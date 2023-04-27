import aws_cdk as cdk

from copper_interface.copper_interface_stack import CopperInterfaceStack


app = cdk.App()
CopperInterfaceStack(
    app,
    "CopperInterfaceStack",
)

app.synth()
