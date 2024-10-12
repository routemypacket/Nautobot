import ipaddress
from nautobot.extras.jobs import Job
from nautobot.ipam.models import IPAddress, Prefix

class CreateOnePrefixFromIPAddresses(Job):
    class Meta:
        name = "Create One Prefix from IP Addresses"
        description = "Browse through all IP addresses and create only one prefix."

    def run(self, data, commit):
        self.log_info("Starting to generate one prefix from IP addresses...")

        # Step 1: Get all IP addresses
        ip_addresses = IPAddress.objects.all()

        # Step 2: Set to store unique prefixes
        prefixes = set()

        # Step 3: Calculate prefixes for each IP address
        for ip in ip_addresses:
            network = ipaddress.ip_network(ip.address, strict=False)
            prefixes.add(network.with_prefixlen)

        # Step 4: Add the first prefix to Nautobot's IPAM if it doesn't exist
        for prefix_str in prefixes:
            if not Prefix.objects.filter(prefix=prefix_str).exists():
                # Create the first new prefix
                Prefix.objects.create(
                    prefix=prefix_str,
                    status='active',
                    description='Auto-created from existing IP addresses'
                )
                self.log_success(f"Successfully created the prefix {prefix_str}.")
                # Stop after creating the first prefix
                return

        self.log_warning("No new prefixes were created. All prefixes already exist.")
