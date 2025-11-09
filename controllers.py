"""
Controllers for CoolProp application (migrated from web2py to py4web)
"""

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import plotly.graph_objects as go
import CoolProp

from py4web import action, request, abort, redirect, URL
from pydal.validators import *
from yatl.helpers import XML, FORM, TABLE, TR, TD, SELECT, INPUT, OPTION, DIV

from .common import db, session, auth, flash

# Template path
template_folder = os.path.join(os.path.dirname(__file__), "templates")

# Input configuration
possible_inputs = [
    ("Density (mass) [kg/m^3]", "Dmass"),
    ("Pressure [Pa]", "P"),
    ("Temperature [K]", "T"),
    ("Enthalpy [J/kg]", "Hmass"),
    ("Entropy [J/kg/K]", "Smass"),
    ("Internal Energy [J/kg]", "Umass"),
    ("Vapor Quality [kg/kg]", "Q"),
]
input_long_strings, input_key_strings = zip(*possible_inputs)
input_longname_to_key = {l: k for l, k in possible_inputs}
input_key_to_longname = {k: l for l, k in possible_inputs}

# Get available fluids
fluids = sorted(CoolProp.__fluids__)


def check_form(form_vars):
    """Validation function for form inputs"""
    errors = {}

    # Check if values are valid numbers
    try:
        value1 = float(form_vars.get("value1", ""))
    except ValueError:
        errors["value1"] = "Value #1 must be a valid number"
        return errors

    try:
        value2 = float(form_vars.get("value2", ""))
    except ValueError:
        errors["value2"] = "Value #2 must be a valid number"
        return errors

    # Check if inputs are valid
    try:
        # Convert input strings to keys
        key1 = CoolProp.CoolProp.get_parameter_index(
            input_longname_to_key[form_vars.get("name1", "")]
        )
        key2 = CoolProp.CoolProp.get_parameter_index(
            input_longname_to_key[form_vars.get("name2", "")]
        )
        # Try to get the pair - validates that these two inputs can be used together
        CoolProp.CoolProp.generate_update_pair(key1, value1, key2, value2)
    except KeyError:
        errors["name1"] = "Invalid input parameter selected"
    except (RuntimeError, ValueError) as e:
        error_msg = str(e)
        if "same input" in error_msg.lower():
            errors["name1"] = "Input #1 and Input #2 must be different"
        else:
            errors[
                "name1"
            ] = "These inputs do not form a valid pair for the selected fluid"

    return errors


@action("index", method=["GET", "POST"])
@action.uses(session, db, auth, "index.html")
def index():
    """Main index page with input form"""

    errors = {}
    form_vars = {}
    error_alert = None  # Always define this

    # Check for flash message from session
    if "error_message" in session and session.get("error_message"):
        error_msg = session.get("error_message")
        error_alert = DIV(
            error_msg,
            _class="alert alert-danger alert-dismissible fade show",
            _role="alert"
        )
        session["error_message"] = None

    if request.method == "POST":
        # Get form data
        form_vars = request.forms

        # Validate
        errors = check_form(form_vars)

        if not errors:
            # Redirect to results page with parameters
            redirect(
                URL(
                    "next",
                    vars=dict(
                        fluid=form_vars.get("fluid"),
                        name1=form_vars.get("name1"),
                        value1=form_vars.get("value1"),
                        name2=form_vars.get("name2"),
                        value2=form_vars.get("value2"),
                        unit_system=form_vars.get("unit_system"),
                    ),
                )
            )

    # Get default or submitted values
    fluid_value = form_vars.get("fluid", "Ammonia")
    name1_value = form_vars.get("name1", "Pressure [Pa]")
    value1_value = form_vars.get("value1", "101325")
    name2_value = form_vars.get("name2", "Temperature [K]")
    value2_value = form_vars.get("value2", "298")
    unit_system_value = form_vars.get("unit_system", "Mass-based")

    # Build form with proper OPTION elements
    error_message = None
    if errors:
        # Display all error messages
        error_msgs = "<br>".join(errors.values())
        error_message = XML(f'<div class="alert alert-danger">{error_msgs}</div>')

    form = FORM(
        error_message if error_message else "",
        TABLE(
            TR(
                TD("Fluid"),
                TD(
                    SELECT(
                        *[
                            OPTION(
                                f,
                                _value=f,
                                _selected="selected" if f == fluid_value else None,
                            )
                            for f in fluids
                        ],
                        _name="fluid",
                    )
                ),
            ),
            TR(
                TD("Input #1"),
                TD(
                    SELECT(
                        *[
                            OPTION(
                                opt,
                                _value=opt,
                                _selected="selected" if opt == name1_value else None,
                            )
                            for opt in input_long_strings
                        ],
                        _name="name1",
                    )
                ),
            ),
            TR(
                TD("Value #1"),
                TD(INPUT(_type="text", _name="value1", _value=value1_value)),
            ),
            TR(
                TD("Input #2"),
                TD(
                    SELECT(
                        *[
                            OPTION(
                                opt,
                                _value=opt,
                                _selected="selected" if opt == name2_value else None,
                            )
                            for opt in input_long_strings
                        ],
                        _name="name2",
                    )
                ),
            ),
            TR(
                TD("Value #2"),
                TD(INPUT(_type="text", _name="value2", _value=value2_value)),
            ),
            TR(
                TD("Output Units"),
                TD(
                    SELECT(
                        OPTION(
                            "Mass-based",
                            _value="Mass-based",
                            _selected="selected"
                            if unit_system_value == "Mass-based"
                            else None,
                        ),
                        OPTION(
                            "Mole-based",
                            _value="Mole-based",
                            _selected="selected"
                            if unit_system_value == "Mole-based"
                            else None,
                        ),
                        _name="unit_system",
                    )
                ),
            ),
            TR(TD(""), TD(INPUT(_type="submit", _value="SUBMIT"))),
        ),
        _method="POST",
    )

    return dict(form=form, error_alert=error_alert)


@action("next")
@action.uses(session, db, auth, "next.html")
def next():
    """Results page showing calculated properties and plot"""

    # Get parameters from request first for error reporting
    fluid = request.params.get("fluid", "")
    name1 = request.params.get("name1", "")
    name2 = request.params.get("name2", "")
    value1_str = request.params.get("value1", "")
    value2_str = request.params.get("value2", "")
    unit_system = request.params.get("unit_system", "Mass-based")

    # Check for errors and redirect if needed
    error_occurred = False

    # Validate required parameters
    if not all([fluid, name1, name2, value1_str, value2_str]):
        session["error_message"] = "Missing required parameters. Please fill out the form."
        error_occurred = True

    # Try to convert values to float
    if not error_occurred:
        try:
            value1 = float(value1_str)
            value2 = float(value2_str)
        except (ValueError, TypeError):
            session["error_message"] = "Invalid number format. Please enter valid numbers."
            error_occurred = True

    # Try to create state and calculate
    if not error_occurred:
        try:
            # Create the state
            HEOS = CoolProp.AbstractState("HEOS", fluid)

            # Convert input strings to keys
            key1 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[name1])
            key2 = CoolProp.CoolProp.get_parameter_index(input_longname_to_key[name2])

            # Update state
            HEOS.update(
                *CoolProp.CoolProp.generate_update_pair(key1, value1, key2, value2)
            )
        except (RuntimeError, ValueError, KeyError) as e:
            # CoolProp error or invalid input - prepare error message
            error_msg = str(e)
            # Make error message more user-friendly
            if "below" in error_msg.lower() or "above" in error_msg.lower():
                user_error = f"Value out of valid range: {error_msg}"
            elif "saturation" in error_msg.lower():
                user_error = f"Invalid state point: {error_msg}"
            else:
                user_error = (
                    f"Cannot calculate state with these inputs: {name1}={value1_str}, "
                    f"{name2}={value2_str}. Error: {error_msg}"
                )

            session["error_message"] = user_error
            error_occurred = True

    # Redirect if any error occurred (do this outside all except blocks)
    if error_occurred:
        redirect(URL("index"))

    # Build results table with proper TD elements
    entries = [
        TR(TD("Temperature [K]"), TD(f"{HEOS.T():.6g}")),
        TR(TD("Pressure [Pa]"), TD(f"{HEOS.p():.6g}")),
        TR(TD("Vapor quality [kg/kg]"), TD(f"{HEOS.keyed_output(CoolProp.iQ):.6g}")),
    ]

    try:
        entries.append(TR(TD("Speed of sound [m/s]"), TD(f"{HEOS.speed_sound():.6g}")))
    except:
        entries.append(TR(TD("Speed of sound [m/s]"), TD("Not valid")))

    if unit_system == "Mole-based":
        entries += [
            TR(TD("Density [mol/m3]"), TD(f"{HEOS.rhomolar():.6g}")),
            TR(TD("Enthalpy [J/mol]"), TD(f"{HEOS.hmolar():.6g}")),
            TR(TD("Entropy [J/mol/K]"), TD(f"{HEOS.smolar():.6g}")),
            TR(
                TD("Constant-pressure specific heat [J/mol/K]"),
                TD(f"{HEOS.cpmolar():.6g}"),
            ),
            TR(
                TD("Constant-volume specific heat [J/mol/K]"),
                TD(f"{HEOS.cvmolar():.6g}"),
            ),
        ]
    elif unit_system == "Mass-based":
        entries += [
            TR(TD("Density [kg/m3]"), TD(f"{HEOS.rhomass():.6g}")),
            TR(TD("Enthalpy [J/kg]"), TD(f"{HEOS.hmass():.6g}")),
            TR(TD("Entropy [J/kg/K]"), TD(f"{HEOS.smass():.6g}")),
            TR(
                TD("Constant-pressure specific heat [J/kg/K]"),
                TD(f"{HEOS.cpmass():.6g}"),
            ),
            TR(
                TD("Constant-volume specific heat [J/kg/K]"),
                TD(f"{HEOS.cvmolar():.6g}"),
            ),
        ]

    form = TABLE(*entries, _class="table table-striped")

    # Create interactive Plotly plot
    T = np.linspace(
        CoolProp.CoolProp.PropsSI(fluid, "Ttriple") + 0.1,
        CoolProp.CoolProp.PropsSI(fluid, "Tcrit") - 0.1,
    )
    p = CoolProp.CoolProp.PropsSI("P", "T", T, "Q", [0] * len(T), fluid)

    # Create Plotly figure
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=T,
            y=p,
            mode="lines",
            name="Saturation Curve",
            line=dict(color="black", width=2),
        )
    )

    fig.update_layout(
        title=f"Pressure-Temperature Saturation Curve for {fluid}",
        xaxis_title="Temperature [K]",
        yaxis_title="Pressure [Pa]",
        yaxis_type="log",
        hovermode="closest",
        template="plotly_white",
    )

    # Convert to HTML div (without full page wrapper)
    fig_html = XML(
        fig.to_html(
            include_plotlyjs="cdn",
            div_id="saturation-plot",
            config={"responsive": True},
        )
    )

    # Get CoolProp version info
    cp_version = CoolProp.__version__
    cp_gitrev = CoolProp.__gitrevision__

    return dict(
        form=form, fig=fig_html, fluid=fluid, cp_version=cp_version, cp_gitrev=cp_gitrev
    )


# Additional routes for compatibility
@action("download/<filename>")
@action.uses(db)
def download(filename):
    """Download handler for uploaded files"""
    # This was in the original web2py app but may not be needed
    abort(404)
