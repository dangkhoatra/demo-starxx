from eth_utils import to_checksum_address, is_checksum_address

class Address:
    def __init__(self, address):
        if not self.is_valid(address):
            raise ValueError("Invalid Ethereum address")
        # Ensure the address is checksummed upon storing
        self._address = to_checksum_address(address)

    @staticmethod
    def is_valid(address):
        """Check if the address is a valid Ethereum address with EIP-55 checksum."""
        return isinstance(address, str) and is_checksum_address(address)

    def with_prefix(self):
        """Return the address with the '0x' prefix in checksum format."""
        return self._address

    def without_prefix(self):
        """Return the address without the '0x' prefix, still in checksum format."""
        return self._address[2:]