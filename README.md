# PHZ//VOID - MikroTik RouterOS Security Framework

Advanced MikroTik RouterOS security assessment and automation framework developed by **PHZ-VOID**.

> ⚠️ For authorized security testing, lab environments, and defensive research only.

---

## Features

- **Authentication Testing**  
  Validate default and custom credential security.

- **Security Assessment**  
  Detect common RouterOS misconfigurations and exposed services.

- **Vulnerability Detection**  
  Identify known RouterOS-related security issues.

- **Router Information Gathering**  
  Collect environment and configuration details for auditing.

- **Automation Utilities**  
  Simplify repetitive security testing workflows.

- **Packet Analysis Support**  
  Network testing powered by **Scapy**.

---

## Requirements

- Python 3.10+
- MikroTik RouterOS target *(authorized environments only)*
- Scapy

---

## Installation

Clone repository:

```bash
git clone https://github.com/aphis-slebew/PHZ-VOID-RouterOS-Toolkit.git
cd PHZ-VOID-RouterOS-Toolkit
```

Install Scapy:

```bash
pip install scapy
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

---

## How To Run

Basic run:

```bash
python phz-void.py
```

Windows example:

```bash
cd /d D:\laragon\www\PHZ-VOID
python phz-void.py
```

If your project supports arguments/options:

Show help menu:

```bash
python phz-void.py --help
```

Interactive mode:

```bash
python phz-void.py --interactive
```

---

## Project Structure

```txt
PHZ-VOID-RouterOS-Toolkit/
│── phz-void.py
│── requirements.txt
│── README.md
│── LICENSE
```

---

## Author

**PHZ-VOID**  
Research & Development by **Aphis Ramadhan**

---

## Notice

This software is intended for:

- Authorized security testing
- Educational purposes
- Defensive research
- Lab simulations

Unauthorized use against systems without permission is strictly prohibited.

Redistribution, re-uploading, or commercial use without permission from **PHZ-VOID** is prohibited.