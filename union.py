#!/usr/bin/env python
# coding=utf-8

import inkex
from inkex.paths import Path
from lxml import etree

class PathOperations(inkex.EffectExtension):

    def union_paths(self, selected_paths):
        """
        Unions the given paths into a single path.

        Args:
            selected_paths (list): A list of Inkscape PathElement objects.

        Returns:
            inkex.PathElement: The resulting unioned path, or None on error.
        """
        combined_path = Path()
        first_path = None  # Store the first path for style copying

        for i, p in enumerate(selected_paths):
            try:
                path_data = p.get('d')
                if path_data:
                    path = Path(path_data)
                    transform = p.composed_transform()
                    if transform is not None:
                        combined_path.append(path.transform(transform))
                    else:
                        combined_path.append(path)
                    if i == 0:
                        first_path = p
                else:
                    inkex.errormsg(f"Path with id '{p.get_id()}' has no path data.")
                    return None
            except Exception as e:
                inkex.errormsg(f"Error processing path with id '{p.get_id()}': {e}")
                return None

        if not combined_path or len(combined_path) == 0:
            return None

        # Create a new path element
        union_path = inkex.PathElement()
        union_path.set('d', combined_path)

        # Copy style from the first selected path
        if first_path is not None:
            union_path.style.update(first_path.style)
        return union_path

    def intersect_paths(self, selected_paths):
        """
        Intersects the given paths, returning the common area.

        Args:
            selected_paths (list): A list of Inkscape PathElement objects.

        Returns:
            inkex.PathElement: The resulting intersection path, or None on error.
        """
        intersected_path = None
        first_path = None

        if not selected_paths:
            return None

        if len(selected_paths) < 2:
            inkex.errormsg("Intersection requires at least two paths.")
            return None

        # Initialize intersected_path with the first path
        try:
            first_path_element = selected_paths[0]
            path_data = first_path_element.get('d')
            if path_data:
                intersected_path = Path(path_data)
                transform = first_path_element.composed_transform()
                if transform:
                    intersected_path = intersected_path.transform(transform)
                first_path = first_path_element
            else:
                inkex.errormsg(f"Path with id '{first_path_element.get_id()}' has no path data.")
                return None
        except Exception as e:
            inkex.errormsg(f"Error processing first path: {e}")
            return None

        # Intersect with the remaining paths
        for p in selected_paths[1:]:
            try:
                path_data = p.get('d')
                if path_data:
                    path = Path(path_data)
                    transform = p.composed_transform()
                    if transform is not None:
                        transformed_path = path.transform(transform)
                    else:
                        transformed_path = path
                    intersected_path = intersected_path.intersect(transformed_path)
                else:
                    inkex.errormsg(f"Path with id '{p.get_id()}' has no path data.")
                    return None
                if not intersected_path:
                    inkex.errormsg("Intersection resulted in an empty path.")
                    return None

            except Exception as e:
                inkex.errormsg(f"Error processing path with id '{p.get_id()}': {e}")
                return None

        # Create a new path element for the intersection
        if intersected_path and len(intersected_path) > 0:
            intersection_path = inkex.PathElement()
            intersection_path.set('d', intersected_path)
            # Copy style from the first selected path
            if first_path:
                intersection_path.style.update(first_path.style)
            return intersection_path
        else:
            return None



    def effect(self):
        # Get selected objects
        selected_objects = self.svg.selection
        selected_paths = []

        if not selected_objects:
            raise inkex.AbortExtension(_("Please select at least two paths to operate on."))

        if len(selected_objects) < 2:
            raise inkex.AbortExtension(_("Please select at least two paths to operate on."))

        for obj_id, obj in selected_objects.items():
            if isinstance(obj, inkex.PathElement):
                selected_paths.append(obj)
            else:
                inkex.errormsg(f"Object with id '{obj_id}' is not a path and will be ignored.")

        if len(selected_paths) < 2:
            raise inkex.AbortExtension(_("Please select at least two path objects to operate on. Ensure objects are converted to paths."))

        # -- User interaction to choose operation --
        # In a real extension, you'd use a dialog, but for simplicity,
        # we'll just check for a parameter named 'operation'
        # Default to 'union' if not provided
        operation = self.options.operation if hasattr(self.options, 'operation') else 'union'

        if operation == 'union':
            result_path = self.union_paths(selected_paths)
        elif operation == 'intersect':
            result_path = self.intersect_paths(selected_paths)
        else:
            inkex.errormsg(f"Unknown operation: {operation}.  Use 'union' or 'intersect'.")
            return

        if result_path is not None:
            # Delete the original paths
            for p in selected_paths:
                p.delete()
            # Add the new path to the document
            self.svg.get_current_layer().append(result_path)
        else:
             inkex.errormsg("Operation failed to produce a path.")

    @staticmethod
    def add_arguments(argparser):
        argparser.add_argument(
            "--operation",
            action="store",
            type=str,
            default="union",  # Default operation
            help="Choose the operation: 'union' or 'intersect'",
        )

if __name__ == '__main__':
    PathOperations().run()