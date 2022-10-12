"""Test if the split basis and weights functions for EcorrNoise and PLRedNoise
and PLDMNoise give the same result as the old code."""

import numpy as np
import pytest
from pint.config import examplefile
from pint.models import get_model_and_toas
from pint.models.timing_model import Component


# get list of correlated noise components
noise_component_labels = []
for key in list(Component.component_types.keys()):
    component_instance = Component.component_types[key]()
    try:
        if component_instance.introduces_correlated_errors:
            noise_component_labels.append(key)
    except:
        pass


def add_DM_noise_to_model(model):
    all_components = Component.component_types
    noise_class = all_components["PLDMNoise"]
    noise = noise_class()  # Make the DM noise instance.
    model.add_component(noise, validate=False)
    model["TNDMAMP"].quantity = 1e-13
    model["TNDMGAM"].quantity = 1.2
    model["TNDMC"].value = 30
    model.validate()
    return model


@pytest.fixture()
def model_and_toas():
    parfile = examplefile("B1855+09_NANOGrav_9yv1.gls.par")
    timfile = examplefile("B1855+09_NANOGrav_9yv1.tim")
    model, toas = get_model_and_toas(parfile, timfile)
    model = add_DM_noise_to_model(model)
    return model, toas


@pytest.mark.parametrize("component_label", noise_component_labels)
def test_noise_basis_shape(model_and_toas, component_label):
    """Test shape of basis matrix."""

    model, toas = model_and_toas
    component = model.components[component_label]
    basis_weight_func = component.basis_funcs[0]

    basis, weights = basis_weight_func(toas)

    assert basis.shape == (len(toas), len(weights))


@pytest.mark.parametrize("component_label", noise_component_labels)
def test_noise_weights_sign(model_and_toas, component_label):
    """Weights should be positive."""

    model, toas = model_and_toas
    component = model.components[component_label]
    basis_weight_func = component.basis_funcs[0]

    basis, weights = basis_weight_func(toas)

    assert np.all(weights >= 0)


@pytest.mark.parametrize("component_label", noise_component_labels)
def test_covariance_matrix_relation(model_and_toas, component_label):
    """Consistency between basis and weights and covariance matrix"""

    model, toas = model_and_toas
    component = model.components[component_label]
    basis_weights_func = component.basis_funcs[0]
    cov_func = component.covariance_matrix_funcs[0]

    basis, weights = basis_weights_func(toas)
    cov = cov_func(toas)
    cov2 = np.dot(basis * weights[None, :], basis.T)

    assert np.allclose(cov, cov2)


def test_ecorrnoise_basis_integer(model_and_toas):
    """ECORR basis matrix contains positive integers."""

    model, toas = model_and_toas
    ecorrcomponent = model.components["EcorrNoise"]

    basis, weights = ecorrcomponent.ecorr_basis_weight_pair(toas)

    assert np.all(basis.astype(int) == basis) and np.all(basis >= 0)


@pytest.mark.parametrize("component_label", ["EcorrNoise", "PLRedNoise"])
def test_noise_basis_weights_funcs(model_and_toas, component_label):
    model, toas = model_and_toas
    component = model.components[component_label]

    basis_weights_func = component.basis_funcs[0]

    basis, weights = basis_weights_func(toas)

    basis_ = component.get_noise_basis(toas)
    weights_ = component.get_noise_weights(toas)

    assert np.allclose(basis_, basis) and np.allclose(weights, weights_)
