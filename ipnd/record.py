import re
from datetime import datetime
from .utils import flatten


class ValidationError(Exception):
    pass


class BaseRecord:
    size = None

    @classmethod
    def flatten(cls, records):
        """
        Flatten child (and grandchild) records
        :param records:
        """
        items = [[r.get_records() if isinstance(r, MultipleRecord) else r for r in record.get_records()]
                 if isinstance(record, MultipleRecord) else [record] for record in records]

        return list(flatten(items))

    def generate_as_dict(self):
        records = self.flatten(self.get_records() if isinstance(self, MultipleRecord) else [self])

        return [record.format_as_dict() for record in records]

    def format_as_dict(self):
        return {
            "type": "N" if isinstance(self, NumericRecord) else "X",
            "size": self.size,
            "value": self.value
        }

    def generate(self):
        records = self.flatten(self.get_records() if isinstance(self, MultipleRecord) else [self])

        return [record.format() for record in records]


class NumericRecord:

    def format(self):
        output = str(self.value).rjust(self.size, "0")

        if len(output) > self.size:
            raise Exception(
                "{} Col is larger than size - {} > {} for {}".format(self, len(output), self.size, self.value))

        return output


class AlphaRecord:

    def format(self):
        return str(self.value)[0:self.size].ljust(self.size, " ")


class SingleRecord(BaseRecord):
    size: int = None

    def __init__(self, value=None):
        self.value = value if value else ""


class MultipleRecord(SingleRecord):

    def get_records(self):
        raise NotImplementedError()


class PublicNumber(SingleRecord, AlphaRecord):
    size = 20


class ServiceStatusCode(SingleRecord, AlphaRecord):
    size = 1

    def __init__(self, value=None):
        if value not in ["C", "D"]:
            raise ValueError("Expected either 'C' or 'D' but got '{}'".format(value))

        super().__init__(value=value)


class UsageCode(SingleRecord, AlphaRecord):
    size = 1



class PendingFlag(SingleRecord, AlphaRecord):
    size = 1


class CancelPendingFlag(SingleRecord, AlphaRecord):
    size = 1


class CustomerSurnameRecord(SingleRecord, AlphaRecord):
    size = 40


class CustomerFirstnameRecord(SingleRecord, AlphaRecord):
    size = 40


class CustomerFirstLongNameRecord(SingleRecord, AlphaRecord):
    size = 120


class CustomerTitleRecord(SingleRecord, AlphaRecord):
    size = 12


class CustomerRawnameRecord(SingleRecord, AlphaRecord):
    size = 160


class CustomerContactNum(SingleRecord, AlphaRecord):
    size = 20


class CustomerName(MultipleRecord):

    def get_records(self):
        if self.value.is_business():
            # Note this is 5.1, 5.2, and 5.3
            return [
                CustomerRawnameRecord(self.value.rawname),
                CustomerTitleRecord(),  # 5.4
            ]

        # It's a person. We return Surname first, then Given and then extended
        return [
            CustomerSurnameRecord(self.value.surname),
            CustomerFirstLongNameRecord("{} {}".format(self.value.firstname, self.value.longname)),
            CustomerTitleRecord(self.value.title),
        ]


class BuildingType(SingleRecord, AlphaRecord):
    size = 6

    def __init__(self, value=None):
        # todo: validate
        self.value = value if value else ""


class BuildingNum(SingleRecord, AlphaRecord):
    size = 5


class BuildingSuffix(SingleRecord, AlphaRecord):
    size = 1


class NumAndSuffixMixin:

    @classmethod
    def get_num_and_suffix(cls, val):

        if val:
            # If we've been given '3A', split it into number and suffix
            match = re.findall("^([\d]+)([^\d]+)$", val)
            if match:
                return int(match[0][0]), match[0][1]
            else:
                return int(val), None

        else:
            return None, None


class BuildingSubUnit(MultipleRecord, NumAndSuffixMixin):

    def __init__(self, building_type=None, street_no_start=None, street_no_end=None):
        self.building_type = BuildingType(value=building_type)

        num, suffix = self.get_num_and_suffix(street_no_start)

        self.building_num_1, self.building_suffix_1 = BuildingNum(num), BuildingSuffix(suffix)

        num, suffix = self.get_num_and_suffix(street_no_end)

        self.building_num_2, self.building_suffix_2 = BuildingNum(num), BuildingSuffix(suffix)

    def get_records(self):
        return [
            self.building_type,
            self.building_num_1,
            self.building_suffix_1,
            self.building_num_2,
            self.building_suffix_2,
        ]


class HouseNum(SingleRecord, AlphaRecord):
    size = 5


class HouseSuffix(SingleRecord, AlphaRecord):
    size = 3


class HouseSuffixSecondary(SingleRecord, AlphaRecord):
    size = 1


class HouseNumberSubunit(MultipleRecord, NumAndSuffixMixin):

    def __init__(self, house_no=None, secondary_no=None):
        num, suffix = self.get_num_and_suffix(house_no)

        self.house_num_1, self.house_suffix_1 = HouseNum(num), HouseSuffix(suffix)

        num, suffix = self.get_num_and_suffix(secondary_no)

        self.house_num_2, self.house_suffix_2 = HouseNum(num), HouseSuffixSecondary(suffix)

    def get_records(self):
        return [
            self.house_num_1,
            self.house_suffix_1,
            self.house_num_2,
            self.house_suffix_2,
        ]


class BuildingFloorType(SingleRecord, AlphaRecord):
    size = 2


class BuildingFloorNr(SingleRecord, AlphaRecord):
    size = 4

    def __init__(self, value=None):

        if value:
            if value > 1000 or value < 1:
                raise ValidationError("Invalid Floor Number: {}".format(value))

        self.value = value if value else ""


class BuildingFloorSuffix(SingleRecord, AlphaRecord):
    size = 1


class BuildingFloor(MultipleRecord):

    def __init__(self, floor=None, floor_type="FL"):

        if not floor:
            self.floor_type = BuildingFloorType()
            self.floor_num = BuildingFloorNr()
            self.floor_suffix = BuildingFloorSuffix()
            return

        self.floor_type = BuildingFloorType(floor_type)

        match = re.findall("^([\d]+)([^\d]+)$", floor)

        if match:
            self.floor_num = BuildingFloorNr(int(match[0][0]))
            self.floor_suffix = BuildingFloorSuffix(match[0][1])
        else:
            self.floor_num = BuildingFloorNr(int(floor))
            self.floor_suffix = BuildingFloorSuffix()

    def get_records(self):

        return [
            self.floor_type,
            self.floor_num,
            self.floor_suffix,
        ]


class BuildingProperty(SingleRecord, AlphaRecord):
    size = 40


class BuildingLocation(SingleRecord, AlphaRecord):
    size = 30


class StreetName(SingleRecord, AlphaRecord):
    size = 25


class StreetType(SingleRecord, AlphaRecord):
    size = 8


class StreetTypeSecondary(SingleRecord, AlphaRecord):
    size = 4


class StreetSuffix(SingleRecord, AlphaRecord):
    size = 6


class StreetSuffixSecondary(SingleRecord, AlphaRecord):
    size = 2


class StreetAddress(MultipleRecord):

    def __init__(self, street_name=None, street_type=None, street_suffix=None):
        self.street_name = StreetName(street_name)
        self.street_type = StreetType(street_type)
        self.street_suffix = StreetSuffix(street_suffix)

        # Not Implemented
        self.street_name_2 = StreetName()
        self.street_type_2 = StreetTypeSecondary()
        self.street_suffix_2 = StreetSuffixSecondary()

    def get_records(self):
        return [
            self.street_name,
            self.street_type,
            self.street_suffix,
            self.street_name_2,
            self.street_type_2,
            self.street_suffix_2,
        ]


class State(SingleRecord, AlphaRecord):
    size = 3


class Locality(SingleRecord, AlphaRecord):
    size = 40


class Postcode(SingleRecord, NumericRecord):
    size = 4


class ServiceLocality(MultipleRecord):

    def __init__(self, state=None, postcode=None, locality=None):
        self.state = State(state)
        self.postcode = Postcode(postcode)
        self.locality = Locality(locality)

    def get_records(self):
        return [
            self.state,
            self.locality,
            self.postcode,

        ]


class Address(MultipleRecord):

    def __init__(self):
        self.building_subunit = BuildingSubUnit()
        self.building_floor = BuildingFloor()
        self.building_property = BuildingProperty()
        self.building_location = BuildingLocation()
        self.house_number_subunit = HouseNumberSubunit()
        self.street_address = StreetAddress()
        self.service_locality = ServiceLocality()

    def set_street_number(self, num: str):
        raise ValidationError("Not House or Building")

    def set_street_name(self, name: str, type: str, suffix: str = ""):
        self.street_address = StreetAddress(street_name=name, street_type=type, street_suffix=suffix)

    def set_locality(self, postcode: str, locality: str, state: str = None):
        self.service_locality = ServiceLocality(postcode=postcode, locality=locality, state=state)

    def get_records(self):
        return [
            self.building_subunit,
            self.building_floor,
            self.building_property,
            self.building_location,
            self.house_number_subunit,
            self.street_address,
            self.service_locality

        ]


class HouseAddress(Address):

    def set_street_number(self, no: str):
        self.house_number_subunit = HouseNumberSubunit(house_no=no)


class BuildingAddress(Address):

    def set_street_number(self, no: str):
        self.building_subunit = BuildingSubUnit(street_no=no)


class BaseAddress(Address):
    def __init__(self, address):
        self.address = address

    def get_records(self):
        return self.address.get_records()

class DirectoryAddress(BaseAddress):
    pass

class ServiceAddress(BaseAddress):
    pass


class CustomFirstName(SingleRecord, AlphaRecord):
    size = 40


class BusinessRawnameRecord(SingleRecord, AlphaRecord):
    size = 80


class FindingTitle(SingleRecord, AlphaRecord):
    size = 12


class FindingName(MultipleRecord):

    def __init__(self, entity):
        self.entity = entity

    def get_records(self):
        if self.entity.is_business():
            return [
                BusinessRawnameRecord(self.entity.rawname),
                FindingTitle()
            ]

        else:
            return [
                CustomerSurnameRecord(self.entity.surname),
                CustomFirstName(self.entity.firstname),
                CustomerTitleRecord(self.entity.title)
            ]




class ListCode(SingleRecord, AlphaRecord):
    size = 2

    # todo: validation


class TypeOfService(SingleRecord, AlphaRecord):
    size: int = 5

    # todo: validation


class CustomerContact(MultipleRecord):

    def __init__(self, entity):
        self.entity = entity

    def get_records(self):
        return [
            CustomerSurnameRecord(self.entity.surname),
            CustomerFirstnameRecord(self.entity.firstname),
            CustomerContactNum(self.entity.contactnum),
        ]


class CSPCode(SingleRecord, AlphaRecord):
    size: int = 3

    def __init__(self, value):
        self.value = value


class DPCode(SingleRecord, AlphaRecord):
    size: int = 6

    def __init__(self, value):
        self.value = value


class DateRecord(SingleRecord, NumericRecord):
    size: int = 14

    def __init__(self, value=None):
        value = value if value else datetime.now()
        value = value.strftime('%Y%m%d%H%M%S')
        super().__init__(value=value)


class TransactionDate(DateRecord):
    pass


class ServiceStatusDate(DateRecord):
    pass


class AlternateAddressFlag(SingleRecord, NumericRecord):
    size: int = 1

    def __init__(self, value="N"):
        super().__init__(value=value)


class PriorPublicNumber(SingleRecord, AlphaRecord):
    size: int = 20


class Entity:
    type: str = 'NA'
    title: str = ""
    rawname: str = ""
    firstname: str = ""
    surname: str = ""
    longname: str = ""
    contactnum: str = ""

    def get_code(self):
        return "N"

    def is_business(self):
        return self.type not in ["PERSON", "NA"]

    def set_contactnum(self, num):
        self.contactnum = num[0:20]

    def set_name(self, name, title=None):
        self.rawname = name[0:160]

        if self.type == "business":
            return

        name_pieces = name.split(" ")

        if not len(name_pieces) > 1:
            raise ValidationError("Expected first/last name")

        # last entry is surname, max = 40 char
        self.surname = name_pieces[-1][0:40]
        self.firstname = name_pieces[0]

        if len(name_pieces) > 2:
            self.longname = " ".join(name_pieces[1:-1])

        self.title = title


class Person(Entity):
    type = "PERSON"

    def get_code(self):
        return "R"


class Business(Entity):
    type = "BUSINESS"

    def get_code(self):
        return "B"


class Govt(Entity):
    type = "GOVT"

    def get_code(self):
        return "G"


class Charity(Entity):
    type = "CHARITY"

    def get_code(self):
        return "C"


class HeaderFooterBase:

    def __init__(self, source: str, seq: int, date=None):

        if seq < 1:
            raise Exception("Invalid Sequence Number {}".format(seq))
        if seq >= 1000000:
            raise Exception("Sequence number {} too high".format(seq))

        self.source = source
        self.seq = seq

        self.date = self.get_date(date if date else datetime.now())

    def get_date(self, date):
        # format = YYYYMMDDHHMMSS
        return date.strftime("%Y%m%d%H%M%S")


class Hdr(SingleRecord, AlphaRecord):
    size = 3

    def __init__(self):
        self.value = "HDR"


class IdnpUp(SingleRecord, AlphaRecord):
    size = 6

    def __init__(self):
        self.value = "IPNDUP"


class Source(SingleRecord, AlphaRecord):
    size = 5


class Sequence(SingleRecord, NumericRecord):
    size = 7


class Date(SingleRecord, NumericRecord):
    size = 14


class HeaderPad(SingleRecord, AlphaRecord):
    size = 870


class Header(HeaderFooterBase, MultipleRecord):

    def get_records(self):
        return [
            Hdr(),
            IdnpUp(),
            Source(self.source),
            Sequence(self.seq),
            Date(self.date),
            HeaderPad()
        ]


class Trl(SingleRecord, AlphaRecord):
    size = 3

    def __init__(self):
        self.value = "TRL"


class Count(SingleRecord, NumericRecord):
    size = 7


class FooterPad(SingleRecord, AlphaRecord):
    size = 874


class Footer(HeaderFooterBase, MultipleRecord):

    def __init__(self, source: str, seq: int, count: int, date=None):
        super().__init__(source=source, seq=seq, date=date)

        if count < 1:
            raise Exception("No rows")
        elif count > 100000:
            raise Exception("More than 100k rows, can't process")

        self.count = count

    def get_records(self):
        return [
            Trl(),
            Sequence(self.seq),
            Date(self.date),
            Count(self.count),
            FooterPad()
        ]


class Transaction(MultipleRecord):
    INDEX = {
        PublicNumber: 1,
        ServiceStatusCode: 2,
        PendingFlag: 3,
        CancelPendingFlag: 4,
        CustomerName: 5,
        FindingName: 6,
        ServiceAddress: 7,
        DirectoryAddress: 8,
        ListCode: 9,
        UsageCode: 10,
        TypeOfService: 11,
        CustomerContact: 12,
        CSPCode: 13,
        DPCode: 14,
        TransactionDate: 15,
        ServiceStatusDate: 16,
        AlternateAddressFlag: 17,
        PriorPublicNumber: 18
    }

    def __init__(self):
        self.t = {}

    def add_entry(self, record: BaseRecord):

        index = self.INDEX[record.__class__]
        self.t[index] = record

    def get_records(self):

        value_classes = [v.__class__ for v in self.t.values()]
        # add defaults
        for k in self.INDEX.keys():
            if k not in value_classes:
                # Will error if required/not default
                try:
                    self.t[self.INDEX[k]] = k()
                except TypeError:
                    raise Exception("Required Transaction record {} not set".format(k))

        records = sorted([(v, k) for k, v in self.t.items()], key=lambda x: x[1])

        return [r[0] for r in records]
