"""
This is a hello world add-on for DocumentCloud.

It demonstrates how to write a add-on which can be activated from the
DocumentCloud add-on system and run using Github Actions.  It receives data
from DocumentCloud via the request dispatch and writes data back to
DocumentCloud using the standard API
"""

import os
import subprocess
from datetime import datetime

from documentcloud.addon import AddOn


class Web3Storage(AddOn):
    """Add-On to upload files to Filecoin via web3.storage"""

    def main(self):

        os.makedirs(f"{os.environ['HOME']}/.config/w3access/")
        with open(
            f"{os.environ['HOME']}/.config/w3access/w3cli.json", "w"
        ) as config_file:
            config_file.write(os.environ["TOKEN"])

        for i, document in enumerate(self.get_documents()):
            self.set_message(f"Uploading {document.title}...")
            print(
                f"{datetime.now()} - Uploading {i} {document.slug} size "
                f"{len(document.pdf)}"
            )
            with open(f"{document.slug}.pdf", "wb") as pdf:
                pdf.write(document.pdf)
            result = subprocess.run(
                ["w3", "up", f"{document.slug}.pdf"], capture_output=True
            )
            if result.returncode != 0:
                self.set_message(f"Error: {result.stderr}")
                raise ValueError(result.stderr)

            link = result.stdout.decode("utf8").strip()[2:]
            document.data["ipfsUrl"] = [link]
            cid = link[link.rfind("/") + 1 :]
            document.data["cid"] = cid
            document.save()
            os.remove(f"{document.slug}.pdf")


if __name__ == "__main__":
    Web3Storage().main()
