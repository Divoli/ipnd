import json
import pprint
from datetime import datetime
from unittest import TestCase
from ipnd.ipnd import IPND
from ipnd import record
from ipnd.utils import flatten


class BaseTests(TestCase):
    @staticmethod
    def dump(data):
        pprint.pprint(data)


class IpndEntityTests(BaseTests):
    """
    IPND Entity Tests
    """

    def test_person(self):
        model = record.Person()

        model.set_contactnum("1234567890")
        model.set_name("John J Smith", "Mr")

        self.assertEqual(model.rawname, "John J Smith")
        self.assertEqual(model.firstname, "John")
        self.assertEqual(model.surname, "Smith")
        self.assertEqual(model.longname, "J")

    def test_business(self):
        model = record.Business()

        self.assertEqual(model.get_code(), "B")


class IpndTransactionEntryTests(BaseTests):
    """
    IPND Transaction Entry Tests
    """

    def test(self):
        record.PublicNumber("0749700000")

    def test_customer_name_person(self):
        entity = record.Person()
        entity.set_name("Herp L. Derpinson", "Mr")
        entity.set_contactnum("0402000000")

        item = record.CustomerName(entity)

        records = item.get_records()

        # Expect PERSON result (3x records)
        self.assertEqual(len(records), 3)

        result = item.generate_as_dict()

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 40, "value": "Derpinson"},
                {"type": "X", "size": 120, "value": "Herp L."},
                {"type": "X", "size": 12, "value": "Mr"},
            ],
        )

    def test_customer_name_business(self):
        entity = record.Business()
        entity.set_name(
            "Extremely Long Name Pty Ltd, Trading as Stupidly Long Name Incorporated"
        )
        entity.set_contactnum("0402000000")

        item = record.CustomerName(entity)

        records = item.get_records()

        # Expect BUSINESS result (2x records)
        self.assertEqual(len(records), 2)

        result = item.generate_as_dict()

        self.assertListEqual(
            result,
            [
                {
                    "type": "X",
                    "size": 160,
                    "value": "Extremely Long Name Pty Ltd, Trading as Stupidly Long Name Incorporated",
                },
                {"type": "X", "size": 12, "value": ""},
            ],
        )

    def test_service_address_building_subunit_default(self):
        item = record.BuildingSubUnit()

        result = item.generate_as_dict()

        # pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 6, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

    def test_service_address_building_subunit(self):
        item = record.BuildingSubUnit(
            building_type="APT", street_no_start="50a", street_no_end="100"
        )

        records = item.get_records()

        # Type + 2x Num/Suffix
        self.assertEqual(len(records), 5)

        result = item.generate_as_dict()

        # pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 6, "value": "APT"},
                {"type": "X", "size": 5, "value": 50},
                {"type": "X", "size": 1, "value": "a"},
                {"type": "X", "size": 5, "value": 100},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

    def test_service_address_building_floor_default(self):
        item = record.BuildingFloor()

        records = item.get_records()

        # Type + 2x Num/Suffix
        self.assertEqual(len(records), 3)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 2, "value": ""},
                {"type": "X", "size": 4, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

    def test_service_address_building_floor(self):
        item = record.BuildingFloor(floor="5a", floor_type="L")

        records = item.get_records()

        # Type + 2x Num/Suffix
        self.assertEqual(len(records), 3)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 2, "value": "L"},
                {"type": "X", "size": 4, "value": 5},
                {"type": "X", "size": 1, "value": "a"},
            ],
        )

    def test_service_address_house_number_subunit_default(self):
        item = record.HouseNumberSubunit()

        records = item.get_records()

        # Type + 2x Num/Suffix
        self.assertEqual(len(records), 4)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 3, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

    def test_service_address_house_number_subunit(self):
        item = record.HouseNumberSubunit(house_no="50a")

        records = item.get_records()

        # Type + 2x Num/Suffix
        self.assertEqual(len(records), 4)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 5, "value": 50},
                {"type": "X", "size": 3, "value": "a"},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

    def test_service_address_street_address(self):
        item = record.StreetAddress(
            street_name="FAKE", street_type="RD", street_suffix="N"
        )

        records = item.get_records()

        # 2x Name/Type/Suffix
        self.assertEqual(len(records), 6)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 25, "value": "FAKE"},
                {"type": "X", "size": 8, "value": "RD"},
                {"type": "X", "size": 6, "value": "N"},
                {"type": "X", "size": 25, "value": ""},
                {"type": "X", "size": 4, "value": ""},
                {"type": "X", "size": 2, "value": ""},
            ],
        )

    def test_service_address_locality(self):
        item = record.ServiceLocality(state="ACT", postcode="0200", locality="ANU")

        records = item.get_records()

        # State/Locality/Postcode
        self.assertEqual(len(records), 3)

        result = item.generate_as_dict()

        # pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 3, "value": "ACT"},
                {"type": "X", "size": 40, "value": "ANU"},
                {"type": "N", "size": 4, "value": "0200"},
            ],
        )


class IpndTransactionServiceAddressTests(BaseTests):
    """
    IPND Transaction Service Address Tests
    """

    def test_service_address(self):
        address = record.HouseAddress()
        address.set_street_number("1")
        address.set_street_name(name="FAKE", type="ST")
        address.set_locality(postcode="0200", locality="ANU", state="ACT")

        records = address.get_records()

        self.assertEqual(len(records), 7)

        self.assertIsInstance(records[0], record.BuildingSubUnit)

        self.assertListEqual(
            records[0].generate_as_dict(),
            [
                {"type": "X", "size": 6, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

        self.assertIsInstance(records[1], record.BuildingFloor)

        self.assertListEqual(
            records[1].generate_as_dict(),
            [
                {"type": "X", "size": 2, "value": ""},
                {"type": "X", "size": 4, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

        self.assertIsInstance(records[2], record.BuildingProperty)

        self.assertEqual(records[2].value, "")

        self.assertIsInstance(records[3], record.BuildingLocation)

        self.assertEqual(records[3].value, "")

        self.assertIsInstance(records[4], record.HouseNumberSubunit)

        self.assertListEqual(
            records[4].generate_as_dict(),
            [
                {"type": "X", "size": 5, "value": 1},
                {"type": "X", "size": 3, "value": ""},
                {"type": "X", "size": 5, "value": ""},
                {"type": "X", "size": 1, "value": ""},
            ],
        )

        self.assertIsInstance(records[5], record.StreetAddress)

        self.assertListEqual(
            records[5].generate_as_dict(),
            [
                {"type": "X", "size": 25, "value": "FAKE"},
                {"type": "X", "size": 8, "value": "ST"},
                {"type": "X", "size": 6, "value": ""},
                {"type": "X", "size": 25, "value": ""},
                {"type": "X", "size": 4, "value": ""},
                {"type": "X", "size": 2, "value": ""},
            ],
        )

        self.assertIsInstance(records[6], record.ServiceLocality)

        pprint.pprint(records[6].generate_as_dict())

        self.assertListEqual(
            records[6].generate_as_dict(),
            [
                {"type": "X", "size": 3, "value": "ACT"},
                {"type": "X", "size": 40, "value": "ANU"},
                {"type": "N", "size": 4, "value": "0200"},
            ],
        )

        records = record.BaseRecord.flatten(records)

        # Expect bunch o sub records
        self.assertEqual(len(records), 23)

        # result = address.generate_as_dict()


class IpndBaseTests(BaseTests):
    def get_date(self):
        # 2020-01-01 00:00
        return datetime.utcfromtimestamp(1577836800)


class IpndHeaderFooterTests(IpndBaseTests):
    """
    IPND Header/Footer Tests
    """

    def test_header(self):
        item = record.Header(source="XXXXX", seq=2, date=self.get_date())

        records = item.get_records()

        self.assertEqual(len(records), 6)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 3, "value": "HDR"},
                {"type": "X", "size": 6, "value": "IPNDUP"},
                {"type": "X", "size": 5, "value": "XXXXX"},
                {"type": "N", "size": 7, "value": 2},
                {"type": "N", "size": 14, "value": "20200101000000"},
                {"type": "X", "size": 870, "value": ""},
            ],
        )

        output = "".join(item.generate())

        self.assertEqual(len(output), 905)

        # get rid of pad for assertion
        output = output.strip()

        self.assertEqual(output, "HDRIPNDUPXXXXX000000220200101000000")

    def test_footer(self):
        item = record.Footer(source="XXXXX", seq=2, count=3, date=self.get_date())

        records = item.get_records()

        self.assertEqual(len(records), 5)

        result = item.generate_as_dict()

        pprint.pprint(result)

        self.assertListEqual(
            result,
            [
                {"type": "X", "size": 3, "value": "TRL"},
                {"type": "N", "size": 7, "value": 2},
                {"type": "N", "size": 14, "value": "20200101000000"},
                {"type": "N", "size": 7, "value": 3},
                {"type": "X", "size": 874, "value": ""},
            ],
        )

        output = "".join(item.generate())

        self.assertEqual(len(output), 905)

        # get rid of pad for assertion
        output = output.strip()

        self.assertEquals(output, "TRL0000002202001010000000000003")


class IpndTransactionTests(IpndBaseTests):
    """
    IPND Transaction Tests
    """

    maxDiff = None

    def get_person(self):
        person = record.Person()
        person.set_name("Herp L. Derpinson", "Mr")
        person.set_contactnum("0402000000")

        return person

    def get_business(self):
        business = record.Business()
        business.set_name(
            "Extremely Long Name Pty Ltd, Trading as Stupidly Long Name Incorporated"
        )
        business.set_contactnum("0402000000")

        return business

    def get_address(self):
        address = record.HouseAddress()
        address.set_street_number("1")
        address.set_street_name("FAKE", "ST")
        address.set_locality("0200", "ANU", "ACT")

        return address

    def test_person_transaction(self):
        person = self.get_person()

        address = self.get_address()

        transaction = record.Transaction()

        transaction.add_entry(record.CSPCode("999"))
        transaction.add_entry(record.DPCode("YYYYYY"))

        transaction.add_entry(record.PublicNumber("0749700000"))
        transaction.add_entry(record.UsageCode(person.get_code()))
        transaction.add_entry(record.ServiceStatusCode("C"))
        transaction.add_entry(record.PendingFlag("N"))
        transaction.add_entry(record.CancelPendingFlag("N"))

        transaction.add_entry(record.CustomerName(person))
        transaction.add_entry(record.FindingName(person))
        transaction.add_entry(record.ServiceAddress(address))
        transaction.add_entry(record.DirectoryAddress(address))

        transaction.add_entry(record.ListCode("UL"))
        transaction.add_entry(record.CustomerContact(person))
        transaction.add_entry(record.TransactionDate(self.get_date()))
        transaction.add_entry(record.ServiceStatusDate(self.get_date()))

        records = transaction.get_records()

        self.assertEquals(len(records), 18)

        flat_records = transaction.generate()

        self.assertEquals(len(flat_records), 68)

        output = "".join(flat_records)

        self.assertEqual(len(output), 905)

        # PublicNumber
        self.assertEqual(records[0].format(), "0749700000          ")
        # ServiceStatusCode
        self.assertEqual(records[1].format(), "C")
        # PendingFlag
        self.assertEqual(records[2].format(), "N")
        # CancelPendingFlag
        self.assertEqual(records[3].format(), "N")

        # CustomerName (multi)
        customer_name = [r.format() for r in records[4].get_records()]

        self.assertEqual(
            customer_name,
            [
                "Derpinson                               ",
                "Herp L.                                                                                                                 ",
                "Mr          ",
            ],
        )

        # FindingName (multi)
        finding_name = [r.format() for r in records[5].get_records()]

        self.assertEqual(
            finding_name,
            [
                "Derpinson                               ",
                "Herp                                    ",
                "Mr          ",
            ],
        )

        # ServiceAddress (multi)
        service_address = [
            r.format() for r in record.BaseRecord.flatten(records[6].get_records())
        ]

        self.assertListEqual(
            service_address,
            [
                "      ",
                "     ",
                " ",
                "     ",
                " ",
                "  ",
                "    ",
                " ",
                "                                        ",
                "                              ",
                "1    ",
                "   ",
                "     ",
                " ",
                "FAKE                     ",
                "ST      ",
                "      ",
                "                         ",
                "    ",
                "  ",
                "ACT",
                "ANU                                     ",
                "0200",
            ],
        )

        # DirectoryAddress (multi)
        directory_address = [
            r.format() for r in record.BaseRecord.flatten(records[7].get_records())
        ]

        self.assertListEqual(
            directory_address,
            [
                "      ",
                "     ",
                " ",
                "     ",
                " ",
                "  ",
                "    ",
                " ",
                "                                        ",
                "                              ",
                "1    ",
                "   ",
                "     ",
                " ",
                "FAKE                     ",
                "ST      ",
                "      ",
                "                         ",
                "    ",
                "  ",
                "ACT",
                "ANU                                     ",
                "0200",
            ],
        )

        # ListCode
        self.assertEqual(records[8].format(), "UL")

        # UsageCode
        self.assertEqual(records[9].format(), "R")

        # TypeOfService
        self.assertEqual(records[10].format(), "     ")

        # CustomerContact (multi)
        customer_contact = [
            r.format() for r in record.BaseRecord.flatten(records[11].get_records())
        ]

        self.assertListEqual(
            customer_contact,
            [
                "Derpinson                               ",
                "Herp                                    ",
                "0402000000          ",
            ],
        )

        # CSPCode
        self.assertEqual(records[12].format(), "999")

        # DPCode
        self.assertEqual(records[13].format(), "YYYYYY")

        # TransactionDate
        self.assertEqual(records[14].format(), "20200101000000")

        # ServiceStatusDate
        self.assertEqual(records[15].format(), "20200101000000")

    def test_transaction(self):
        person = self.get_person()

        business = self.get_business()

        address = self.get_address()

        # This is the File Sequence Number
        i = IPND(source="XXXXX", seq=2, date=self.get_date())

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
            t.add_entry(record.TransactionDate(self.get_date()))
            t.add_entry(record.ServiceStatusDate(self.get_date()))

            i.add_transaction(t)

        result = i.generate()

        # header/footer + 2 rows
        self.assertEqual(len(result), 4)

        header = "".join(result[0]).strip()

        self.assertEqual(header, "HDRIPNDUPXXXXX000000220200101000000")

        footer = "".join(result[-1]).strip()

        self.assertEqual(footer, "TRL0000002202001010000000000002")

        output = i.generate_to_string()

        self.assertEqual(len(output), 905 * 4)
