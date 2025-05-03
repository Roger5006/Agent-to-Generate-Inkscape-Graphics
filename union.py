#!/usr/bin/env python
# coding=utf-8

import inkex
from inkex.paths import Path
from lxml import etree

class UnionPaths(inkex.EffectExtension):

    def effect(self):
        # Get selected objects
        selected_objects = self.svg.selection
        selected_paths = []

        if not selected_objects:
            raise inkex.AbortExtension(_("Please select at least two paths to union."))

        if len(selected_objects) < 2:
            raise inkex.AbortExtension(_("Please select at least two paths to union."))

        for obj_id, obj in selected_objects.items():
            if isinstance(obj, inkex.PathElement):
                selected_paths.append(obj)
            else:
                inkex.errormsg(f"Object with id '{obj_id}' is not a path and will be ignored.")

        if len(selected_paths) < 2:
            raise inkex.AbortExtension(_("Please select at least two path objects to union. Ensure objects are converted to paths."))

        combined_path = Path()

        for p in selected_paths:
            try:
                path_data = p.get('d')
                if path_data:
                    path = Path(path_data)
                    transform = p.composed_transform()
                    if transform is not None:
                        combined_path.append(path.transform(transform))
                    else:
                        combined_path.append(path)
                else:
                    inkex.errormsg(f"Path with id '{p.get_id()}' has no path data.")
            except Exception as e:
                inkex.errormsg(f"Error processing path with id '{p.get_id()}': {e}")

            # Delete the original paths
            p.delete()

        # Create a new path element
        union_path = inkex.PathElement()
        union_path.set('d', combined_path)

        # Copy style from the first selected path
        if selected_paths:
            union_path.style.update(selected_paths[0].style)

        # Add the new path to the document
        self.svg.get_current_layer().append(union_path)

if __name__ == '__main__':
    UnionPaths().run()