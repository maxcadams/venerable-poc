def lookup(alias, alias_set):
    """
    Performs a party look up by alias in alias_set.

    :param alias: Alias of party we are looking up.
    :param alias_set: Alias set in which party resides.
    :return: Party information
    """
    pass

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

def build_VLP(transaction):
    """
    Builds the VenerableLedgerProcessing section of a PaymentInstruction.

    :param transaction: Transaction data being used to build section.
    :return: VLP section.
    """
    pass

def build_ContextSource(transaction):
    """
    Builds the ContextSource section of a PaymentInstruction. 

    :param transaction: Transaction data being used to build section.
    :return: ContextSource section.
    """
    pass


def build_PaymentInstruction(transaction, payment_instructions):
    """
    Builds payment instruction item using transaction and appends it 
    to payment_instructions.

    :param transaction: Transaction entry from source.
    :param payment_instructions: List of payment_instructions.
    :return: updated payment instructions
    """
    pass


def build_PaymentInstruction(transaction, payment_instructions):
    """
    Builds payment instruction item using transaction and appends it 
    to payment_instructions.

    :param transaction: Transaction entry from source.
    :param payment_instructions: List of payment_instructions.
    :return: updated payment instructions --> is this necessary???
    """
    pi = {
        "PaymentInstruction": {}
    }
    PaymentInstruction = pi['PaymentInstruction']
    PaymentInstruction['ContextSource'] = build_ContextSource(transaction)
    PaymentInstruction['VenerableLedgerProcessing'] = build_VLP(transaction)
    PaymentInstruction['PaymentInfo'] = build_PaymentInfo(transaction)
    PaymentInstruction['PayeeDetails'] = build_PayeeDetails(transaction)
    
    payment_instructions.append(pi)
    return

def build_domain():
    """
    Builds outer skeleton of domain for payment instructions.
    """
    transactions = {
        'Transactions': {
            'SchemaVersion': 'v1.0',
            'PaymentInstructions': []
        }
    }
    
    payment_instructions : list = transactions['Transactions']['PaymentInstructions']
    
    return transactions