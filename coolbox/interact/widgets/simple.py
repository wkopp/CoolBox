from ipywidgets import (
    HBox, VBox, Label, Dropdown, Button, Label,
    Checkbox, FloatText,
    Text, Image, IntRangeSlider, Layout
)

from coolbox.utilities import (
    GenomeRange
)
from .base import WidgetsBox

from collections import OrderedDict

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class SimpleWidgets(WidgetsBox):
    """
    Simplest widgets panel design.

    Layout:

    -----------------------------------------------------------------------------------------
    left_button | right_button | zoom_out_button | zoom_in_button | range_textbox | go_button
    -----------------------------------------------------------------------------------------
    range_min_label | range_slider | range_max_label
    --------------------------------------------------------------------
    auto_check_box | track_min_val_float_text | track_max_val_float_text
    --------------------------------------------------------------------
    frame
    -----

    """
    def __init__(self, *args, **kwargs):
        """
        Args:
            browser (:obj:`BrowserBase`): Browser object.
        """
        self.browser = args[0]

        self.widgets_dict = self.get_widgets_dict()
        self.refresh_widgets()
        self.panel = self.compose_panel(self.widgets_dict)
        self.register_events_handler()

    def get_widgets_dict(self):
        widgets = OrderedDict([
            ("chromosomes_list",          Dropdown(options=self.browser.chrom_lengthes.keys())),
            ("left_button",               Button(icon="arrow-left")),
            ("right_button",              Button(icon="arrow-right")),
            ("zoom_out_button",           Button(icon="search-minus")),
            ("zoom_in_button",            Button(icon="search-plus")),
            ("range_textbox",             Text(placeholder="genome range like: 'chr1:10000-20000'")),
            ("go_button",                 Button(description="Go")),

            ("range_slider",              IntRangeSlider(continuous_update=False, readout=False, layout=Layout(width='90%'))),
            ("range_min_label",           Label("", layout=Layout(width='2%'))),
            ("range_max_label",           Label("", layout=Layout(width='20%'))),

            ("auto_check_box",            Checkbox(value=True, description="Auto Range",
                                                   layout=Layout(width='120px'),
                                                   style={'description_width': 'initial'})),
            ("track_min_val_float_text",  FloatText(value=0,  description="track's min value:", step=0.5, disabled=True,
                                                    layout=Layout(width='30%'),
                                                    style={'description_width': 'initial'})),
            ("track_max_val_float_text",  FloatText(value=10, description="track's max value:", step=0.5, disabled=True,
                                                    layout=Layout(width='30%'),
                                                    style={'description_width': 'initial'})),

            ("frame",                     Image())
        ])
        return widgets

    def refresh_widgets(self, who=None):
        range_ = self.browser.current_range
        max_ = self.browser.chrom_lengthes[range_.chrom]
        # update range_textbox
        if who != "go_button":
            self.widgets_dict['range_textbox'].value = str(range_)
        # update range_slider
        if who != "range_slider":
            slider = self.widgets_dict['range_slider']
            slider.min = 1
            slider.max = max_
            slider.value = (range_.start, range_.end)
        # update chromosome list
        if who != "chromosomes_list":
            self.widgets_dict['chromosomes_list'].value = range_.chrom
        # update range max min label
        self.widgets_dict['range_min_label'].value = str(1)
        self.widgets_dict['range_max_label'].value = str(max_)

    def compose_panel(self, widgets_dict):
        panel = VBox([
            VBox([
                HBox(list(widgets_dict.values())[:7]),
                HBox([
                    widgets_dict["range_min_label"],
                    widgets_dict["range_slider"],
                    widgets_dict["range_max_label"],
                ]),
                HBox([
                    widgets_dict["auto_check_box"],
                    widgets_dict["track_min_val_float_text"],
                    widgets_dict["track_max_val_float_text"],
                ], layout=Layout(justify_content="flex-start")),
            ], layout=Layout(border='solid 2px')),
            widgets_dict["frame"],
        ])
        return panel

    def register_events_handler(self):

        # chromosomes_list value change
        def chrom_dropdown_val_change(change):
            new_chrom = change['new']
            current_range = self.browser.current_range
            # only change chromosome
            range_ = GenomeRange(new_chrom, current_range.start, current_range.end)
            range_ = self.browser.chrom_lengthes.bound_range(range_)
            self.browser.goto(range_, who='chromosomes_list')
            self.browser.refresh()
        self.widgets_dict['chromosomes_list'].observe(chrom_dropdown_val_change, names="value")

        # left_button click
        def left_button_click(b):
            self.browser.go_left()
            self.browser.refresh()
        #            self.browser.preload_imgs('left')
        self.widgets_dict['left_button'].on_click(left_button_click)

        # right_button click
        def right_button_click(b):
            self.browser.go_right()
            self.browser.refresh()
        #            self.browser.preload_imgs('right')
        self.widgets_dict['right_button'].on_click(right_button_click)

        # zoom_in_button click
        def zoom_in_button_click(b):
            self.browser.zoom_in()
            self.browser.refresh()
        #            self.browser.preload_imgs('zoom-in')
        self.widgets_dict['zoom_in_button'].on_click(zoom_in_button_click)

        # zoom_out_button click
        def zoom_out_button_click(b):
            self.browser.zoom_out()
            self.browser.refresh()
        #            self.browser.preload_imgs('zoom-out')
        self.widgets_dict['zoom_out_button'].on_click(zoom_out_button_click)

        # go_button click
        def go_button_click(b):
            range_str = self.widgets_dict['range_textbox'].value.strip("'")
            range_ = GenomeRange(range_str)
            self.browser.goto(range_, who='go_button')
            self.browser.refresh()
        self.widgets_dict['go_button'].on_click(go_button_click)

        # range_slider value change
        def range_slider_val_change(change):
            start_old, end_old = change['old']
            length_old = end_old - start_old

            start, end = change['new']
            chrom = self.browser.current_range.chrom
            if end - start <= 0:
                end = start + length_old
            new_range = GenomeRange(chrom, start, end)
            new_range = self.browser.chrom_lengthes.bound_range(new_range)
            self.browser.goto(new_range, who='range_slider')
            self.browser.refresh()
        self.widgets_dict['range_slider'].observe(range_slider_val_change, names="value")

        # auto_check_box value change
        def auto_check_box_val_change(change):
            if change['new'] == True:
                self.widgets_dict['track_min_val_float_text'].disabled = True
                self.widgets_dict['track_max_val_float_text'].disabled = True
                self.browser.frame.set_tracks_min_max('auto', 'auto')
            else:
                self.widgets_dict['track_min_val_float_text'].disabled = False
                self.widgets_dict['track_max_val_float_text'].disabled = False
                min_ = self.widgets_dict['track_min_val_float_text'].value
                max_ = self.widgets_dict['track_max_val_float_text'].value
                self.browser.frame.set_tracks_min_max(min_, max_)
            self.browser.clear_fig_cache()
            self.browser.refresh()
        self.widgets_dict['auto_check_box'].observe(auto_check_box_val_change, names="value")

        # track_max_value_float_text value change and
        #   track_min_value_float_text value change
        def track_float_text_val_change(change):
            min_ = self.widgets_dict['track_min_val_float_text'].value
            max_ = self.widgets_dict['track_max_val_float_text'].value
            self.browser.frame.set_tracks_min_max(min_, max_)
            self.browser.clear_fig_cache()
            self.browser.refresh()
        self.widgets_dict['track_min_val_float_text'].observe(track_float_text_val_change, names="value")
        self.widgets_dict['track_max_val_float_text'].observe(track_float_text_val_change, names="value")

