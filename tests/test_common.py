from dataclasses import dataclass

import msgpack
import pytest

from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass
class EntityA1(DataClassDictMixin):
    x: int


@dataclass
class EntityA2(EntityA1):
    y: int


@dataclass
class EntityA1Wrapper(DataClassMessagePackMixin):
    entity: EntityA1


@dataclass
class EntityA2Wrapper(DataClassMessagePackMixin):
    entity: EntityA2


@dataclass
class EntityB1(DataClassDictMixin):
    x: int


@dataclass
class EntityB2(EntityB1):
    y: int


@dataclass
class EntityB1WrapperDict(DataClassDictMixin):
    entity: EntityB1


@dataclass
class EntityB2WrapperMessagePack(DataClassMessagePackMixin):
    entity: EntityB2


@dataclass
class EntityBWrapperMessagePack(DataClassMessagePackMixin):
    entity1wrapper: EntityB1WrapperDict
    entity2wrapper: EntityB2WrapperMessagePack


def test_slots():
    @dataclass
    class RegularDataClass:
        __slots__ = ("number",)
        number: int

    @dataclass
    class DictDataClass(DataClassDictMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class JSONDataClass(DataClassJSONMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class MessagePackDataClass(DataClassMessagePackMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class YAMLDataClass(DataClassYAMLMixin):
        __slots__ = ("number",)
        number: int

    for cls in (
        RegularDataClass,
        DictDataClass,
        JSONDataClass,
        MessagePackDataClass,
        YAMLDataClass,
    ):
        instance = cls(1)
        with pytest.raises(AttributeError) as e:
            instance.new_attribute = 2
        assert (
            str(e.value)
            == f"'{cls.__name__}' object has no attribute 'new_attribute'"
        )


def test_data_class_dict_mixin_from_dict():
    assert DataClassDictMixin.from_dict({}) is None


def test_data_class_dict_mixin_to_dict():
    assert DataClassDictMixin().to_dict() is None


def test_compiled_mixin_with_inheritance_1():
    entity = EntityA2(x=1, y=2)
    wrapper = EntityA2Wrapper(entity)
    data = msgpack.packb({"entity": {"x": 1, "y": 2}}, use_bin_type=True)
    assert wrapper.to_msgpack() == data
    assert EntityA2Wrapper.from_msgpack(data) == wrapper


def test_compiled_mixin_with_inheritance_2():
    entity1w = EntityB1WrapperDict(EntityB1(x=1))
    entity2w = EntityB2WrapperMessagePack(EntityB2(x=1, y=2))
    wrapper = EntityBWrapperMessagePack(entity1w, entity2w)
    data = msgpack.packb(
        {
            "entity1wrapper": {"entity": {"x": 1}},
            "entity2wrapper": {"entity": {"x": 1, "y": 2}},
        },
        use_bin_type=True,
    )
    assert wrapper.to_msgpack() == data
    assert EntityBWrapperMessagePack.from_msgpack(data) == wrapper
