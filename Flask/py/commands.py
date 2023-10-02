class CommandHandler:
    def __init__(self):
        self.commands = {
            "communication check": "PPPPP",
            "launch imminent": "GGGGG",
            "abort": "ABORT",
            "separate": "SSSSS",
            "deploy main": "MMMMM"
        }

    def execute(self,command,tlmService):
        command = command.lower().strip()
        err=None
        output=""
        """
        if not tlmService.alive:
            err="Telemetry service is not alive."
            print(err)
            return err
        """
        if command in self.commands:
            tlmService.send_command(self.commands[command])
            output="Sent command: %s" % self.commands[command]
        else:
            err="Command not found."
            print(err)
        
        return output,err
