from collections import OrderedDict

from django import forms
from django.forms import widgets
from django.utils.functional import cached_property

from wagtail.admin.staticfiles import versioned_static
from wagtail.telepath import Adapter, register

from .base import DeclarativeSubBlocksMetaclass, get_help_icon
from .field_block import ChoiceBlock
from .struct_block import BaseStructBlock, StructValue


class UnionValue:
    ...


class UnionBlock(BaseStructBlock, metaclass=DeclarativeSubBlocksMetaclass):
    def __init__(self, local_blocks=None, *args, **kwargs):
        super().__init__(local_blocks=local_blocks, *args, **kwargs)
        selector_block = ChoiceBlock(
            default=list(self.child_blocks.values())[0].name,
            choices=[(b.name, b.label) for b in self.child_blocks.values()],
            widget=widgets.RadioSelect(),
            label="Type",
        )
        selector_block.set_name("__union_type__")
        self.child_blocks = OrderedDict(
            __union_type__=selector_block, **self.child_blocks
        )

    class Meta:
        default = {}
        form_classname = "union-block"
        form_template = None
        value_class = StructValue
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
