import numpy as np
import gradio as gr
import json

def pdb_format_string(coords, types, a, b, c, alpha, beta, gamma, model=1):
    """
    Return string in the protein databank atomic structure format.
    Includes CRYST1, ATOM, ENDMDL, and END records for py3Dmol compatibility.
    """
    # CRYST1 record following strict PDB specification
    # CRYST1  a       b       c    alpha   beta  gamma space_group Z
    # Example: CRYST1  7.382   7.382   7.382  90.00  90.00  90.00 P 1           1
    # Field widths: a,b,c (8.3f), alpha,beta,gamma (7.2f), P 1 (10 chars), Z (3 chars)
    header = ("CRYST1{:8.3f}{:8.3f}{:8.3f}"
              "{:7.2f}{:7.2f}{:7.2f} P 1       1\n"
              "MODEL     {:d}\n").format(a, b, c, alpha, beta, gamma, model)

    # ATOM record following strict PDB specification
    atom_line_format = ("ATOM  {0:5d} {1:<4s}{2:3s} {3:1s}{4:4d}    {5:8.3f}{6:8.3f}{7:8.3f}"
                        "{8:6.2f}{9:6.2f}          {10:<2s}\n")


    out = header
    for i, coo in enumerate(coords):
        # PDB ATOM serial numbers are 1-indexed
        atom_name_padded = types[i].ljust(4)
        element_padded = types[i].ljust(2)

        out += atom_line_format.format(i + 1, atom_name_padded, 'ATM', 'A', 1,
                                        coo[0], coo[1], coo[2], 1.00, 0.00, element_padded)

    out += "ENDMDL\n"
    out += "END\n"
    return out

def get_atom_color(symbol):
    """
    Return display color for an atomic symbol.
    """
    colors = {
        "H": "white", "He": "cyan", "Li": "purple", "C": "black", "O": "red",
        "N": "blue", "Si": "yellow", "Fe": "orange", "Na": "blue", "Cl": "green",
    }
    return colors.get(symbol, "gray")

def plot_crystal_structure_to_html(phase):
    """
    Generate custom HTML string to render crystal structure with 3Dmol.js via py3Dmol PDB format.
    """
    lattice_constant = phase["lattice"]
    lattice_vectors = np.array(phase["lattice_vector"])

    xyz_coords = np.array(phase["xyz"])
    symbols = phase["symbol"]
    coordinates_type = phase.get("coordinates_type", "fractional")

    if coordinates_type == "fractional":
        cartesian_basis_vectors = lattice_vectors * lattice_constant
        cartesian_coords = np.dot(xyz_coords, cartesian_basis_vectors)
    elif coordinates_type == "cartesian":
        cartesian_coords = xyz_coords
    else:
        raise ValueError("coordinates_type must be 'fractional' or 'cartesian'.")

    a_len = lattice_constant
    b_len = lattice_constant
    c_len = lattice_constant
    alpha_deg = 90.0
    beta_deg = 90.0
    gamma_deg = 90.0

    pdb_string = pdb_format_string(
        cartesian_coords, symbols,
        a_len, b_len, c_len, alpha_deg, beta_deg, gamma_deg
    )

    import py3Dmol

    view = py3Dmol.view(width=600, height=400)
    view.addModel(pdb_string, 'pdb', {'doAssembly': True, 'bonds': True})
    view.setStyle({"model": 0}, {"sphere": {"radius": 0.7, "colorscheme": {"prop": "atom", "map": {s: get_atom_color(s) for s in set(symbols)}}}})

    for i, (coord, symbol) in enumerate(zip(cartesian_coords, symbols)):
        x, y, z = coord
        view.addLabel(symbol, {'position': {'x': float(x), 'y': float(y), 'z': float(z) + 1.0}, 'fontColor': 'black', 'fontSize': 10})

    view.zoomTo()

    html_content = view._make_html()
    escaped_html_string = html_content.replace("'", "&#x27;") 
    iframe_html = f'<iframe srcdoc=\'{escaped_html_string}\' width="100%" height="600px" frameborder="0" allowfullscreen sandbox="allow-scripts allow-same-origin"></iframe>'
    return iframe_html

# Example 1: NaCl unit cell
nacl_phase = {
    "lattice": 5.64,  # Å
    "lattice_vector": [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ],
    "xyz": [
        [0, 0, 0],       # Na
        [0.5, 0.5, 0.5], # Cl
        [0.5, 0, 0],     # Cl
        [0, 0.5, 0],     # Cl
        [0, 0, 0.5],     # Cl
        [0.5, 0.5, 0],   # Na
        [0.5, 0, 0.5],   # Na
        [0, 0.5, 0.5]    # Na
    ],
    "symbol": [
        "Na", "Cl", "Cl", "Cl", "Cl", "Na", "Na", "Na"
    ],
    "coordinates_type": "fractional"
}

# Example 2: Silicon (Si) diamond unit cell
si_phase = {
    "lattice": 5.43,  # Å
    "lattice_vector": [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ],
    "xyz": [
        [0, 0, 0],
        [0.5, 0.5, 0],
        [0.5, 0, 0.5],
        [0, 0.5, 0.5],
        [0.25, 0.25, 0.25],
        [0.75, 0.75, 0.25],
        [0.75, 0.25, 0.75],
        [0.25, 0.75, 0.75]
    ],
    "symbol": [
        "Si", "Si", "Si", "Si", "Si", "Si", "Si", "Si"
    ],
    "coordinates_type": "fractional"
}

def create_gradio_app(phase_data):
    html_output = plot_crystal_structure_to_html(phase_data)
    return html_output

with gr.Blocks() as demo:
    gr.Markdown("# Crystal Structure Viewer")
    with gr.Row():
        with gr.Column():
            gr.Markdown("## NaCl Structure")
            nacl_html_display = gr.HTML(value=create_gradio_app(nacl_phase), label="NaCl Structure")
        with gr.Column():
            gr.Markdown("## Silicon Structure")
            si_html_display = gr.HTML(value=create_gradio_app(si_phase), label="Silicon Structure")

if __name__ == "__main__":
    demo.launch()