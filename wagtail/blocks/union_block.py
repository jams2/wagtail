from collections import OrderedDict

from django import forms
from django.forms import widgets
from django.utils.functional import cached_property

from wagtail.admin.staticfiles import versioned_static
from wagtail.telepath import Adapter, register

from .base import DeclarativeSubBlocksMetaclass, get_help_icon
from .field_block import ChoiceBlock
from .struct_block import BaseStructBlock, StructValue


class UnionValue(StructValue):
    pass


class UnionBlock(BaseStructBlock, metaclass=DeclarativeSubBlocksMetaclass):
    def __init__(self, local_blocks=None, default_type=None, *args, **kwargs):
        super().__init__(local_blocks=local_blocks, *args, **kwargs)

        if not default_type:
            default_type = next(self.child_blocks.values()).name
        elif default_type not in self.child_blocks:
            raise ValueError("default_type must be the name of one of the UnionBlock's members")

        selector_block = ChoiceBlock(
            default=default_type,
            choices=[(b.name, b.label) for b in self.child_blocks.values()],
            widget=widgets.RadioSelect(),
            label="Type",
        )
        selector_block.set_name("__union_type__")
        self.child_blocks = OrderedDict(
            __union_type__=selector_block, **self.child_blocks
        )

    def value_from_datadict(self, data, files, prefix):
        selected_type = data.get(f"{prefix}-__union_type__")
        return self._to_struct_value(
            [
                (
                    name,
                    block.value_from_datadict(data, files, f"{prefix}-{name}"),
                )
                for name, block in self.child_blocks.items()
                if name in ("__union_type__", selected_type)
            ]
        )

    class Meta:
        default = {}
        form_classname = "union-block"
        form_template = None
        value_class = UnionValue
        label_format = None
        icon = "placeholder"


class UnionBlockAdapter(Adapter):
    js_constructor = "wagtail.blocks.UnionBlock"

    def js_args(self, block):
        meta = {
            "label": block.label,
            "required": block.required,
            "icon": block.meta.icon,
            "classname": block.meta.form_classname,
        }

        help_text = getattr(block.meta, "help_text", None)
        if help_text:
            meta["helpText"] = help_text
            meta["helpIcon"] = get_help_icon()

        if block.meta.form_template:
            meta["formTemplate"] = block.render_form_template()

        if block.meta.label_format:
            meta["labelFormat"] = block.meta.label_format

        return [
            block.name,
            block.child_blocks.values(),
            meta,
        ]

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailadmin/js/telepath/blocks.js"),
            ]
        )


register(UnionBlockAdapter(), UnionBlock)
