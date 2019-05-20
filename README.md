# Australian IPND (Integrated Public Number Database) Client

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)


This is a python 3 port of [xrobau/ipnd](https://github.com/xrobau/ipnd)

Many thanks to this author!~

Licenced under the AGPLv3.

You can install this module via pip:


```
pip install au-ipnd
```


Example Code

```

from ipnd import record, IPND

person = record.Person()
person.set_name("Herp L. Derpinson", "Mr")
person.set_contactnum("0402000000")

business = record.Business()
business.set_name("Extremely Long Name Pty Ltd, Trading as Stupidly Long Name Incorporated")
business.set_contactnum("0402000000")

address = record.HouseAddress()
address.set_street_number("1")
address.set_street_name("FAKE", "ST")
address.set_locality("0200", "ANU", "ACT")

# This is the File Sequence Number
i = IPND(source="XXXXX", seq=2)

nums = (("0749700000", person), ("0749700001", business))

for num, entity in nums:
    t = record.Transaction()

    t.add_entry(record.CSPCode("999"))
    t.add_entry(record.DPCode("YYYYYY"))

    t.add_entry(record.PublicNumber(num))
    t.add_entry(record.UsageCode(entity))
    t.add_entry(record.ServiceStatusCode("C"))
    t.add_entry(record.PendingFlag("N"))
    t.add_entry(record.CancelPendingFlag("N"))
    t.add_entry(record.CustomerName(entity))
    t.add_entry(record.FindingName(entity))
    t.add_entry(record.ServiceAddress(address))
    t.add_entry(record.DirectoryAddress(address))

    t.add_entry(record.ListCode("UL"))
    t.add_entry(record.CustomerContact(entity))

    i.add_transaction(t)

output = i.generate_to_string()

print(output)

```

