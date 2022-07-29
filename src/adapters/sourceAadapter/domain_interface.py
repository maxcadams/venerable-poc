def build_PayeeDetails(transaction):
    """
    Builds the PayeeDetails section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PayeeDetails section.
    """
    pass


def build_PaymentInfo(transaction):
    """
    Builds the PaymentInfo section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: PaymentInfo section.
    """
    pass


def build_CLP(transaction):
    """
    Builds the CompanyLedgerProcessing section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: CLP section.
    """
    pass


def build_ContextSource(transaction):
    """
    Builds the ContextSource section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: ContextSource section.
    """
    pass


def build_PaymentInstruction(transaction):
    """
    Builds payment instruction item using transaction and appends it
    to payment_instructions.

    :param transaction: Transaction entry from source.
    :param payment_instructions: List of payment_instructions.
    :return: payment instruction created
    """
    pi = {"PaymentInstruction": {}}
    PaymentInstruction = pi["PaymentInstruction"]
    PaymentInstruction["ContextSource"] = build_ContextSource(transaction)
    PaymentInstruction["CompanyLedgerProcessing"] = build_CLP(transaction)
    PaymentInstruction["PaymentInfo"] = build_PaymentInfo(transaction)
    PaymentInstruction["PayeeDetails"] = build_PayeeDetails(transaction)

    return pi


def build_domain(transactions: list):
    """
    Builds outer skeleton of domain for payment instructions.

    :param transactions: transactions from sourceA (list)
    """
    final = {"Transactions": {"SchemaVersion": "v1.0", "PaymentInstructions": []}}

    # builds list using list comprehension
    final["Transactions"]["PaymentInstructions"] = [
        build_PaymentInstruction(transaction) for transaction in transactions
    ]

    return final
