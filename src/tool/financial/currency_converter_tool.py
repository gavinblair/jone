from ..abstract_tool import AbstractTool

class CurrencyConverterTool(AbstractTool):
    def __init__(self):
        super().__init__(
            name="CurrencyConverter",
            description="Converts an amount from one currency to another.",
            toolset="Financial",
            command_template="python3 ./src/tool/financial/scripts/currency_conversion.py -a {amount} -f {from_currency} -t {to_currency}",
            can_be_triggered_by_voice_command=False,
            display_command_output_to_user=False
        )
        self.define_arguments()

    def define_arguments(self):
        self.add_argument('amount', float, True, "What amount would you like to convert?")
        self.add_argument('from_currency', str, True, "Which currency are you converting from?")
        self.add_argument('to_currency', str, True, "Which currency are you converting to?")


