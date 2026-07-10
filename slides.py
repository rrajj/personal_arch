import copy
from pptx import Presentation
from pptx.oxml.ns import qn

def duplicate_slide(prs, slide_index):
    """Duplicate the slide at slide_index and append it to the end. Returns new slide."""
    source = prs.slides[slide_index]
    blank_layout = source.slide_layout
    new_slide = prs.slides.add_slide(blank_layout)

    # remove any placeholder shapes add_slide() created, we'll copy the real ones
    for shape in list(new_slide.shapes):
        shape._element.getparent().remove(shape._element)

    # copy all shapes from source slide
    for shape in source.shapes:
        new_el = copy.deepcopy(shape._element)
        new_slide.shapes._spTree.append(new_el)

    # copy images/media relationships (so pictures don't break)
    for rel_id, rel in source.part.rels.items():
        if "image" in rel.reltype:
            new_slide.part.rels.add_relationship(
                rel.reltype, rel.target_part, rel_id
            )

    return new_slide

def build_slide(prs, source_index, keep_shape_names):
    """Duplicate a slide, keeping only shapes whose name is in keep_shape_names."""
    new_slide = duplicate_slide(prs, source_index)
    for shape in list(new_slide.shapes):
        if shape.name not in keep_shape_names:
            shape._element.getparent().remove(shape._element)
    return new_slide
