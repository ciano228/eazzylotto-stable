"""
Tests unitaires pour le service Katula complet
"""
import pytest
from katula_complete_service import KatulaCompleteService, ChipCompartment

@pytest.fixture
def katula_service():
    return KatulaCompleteService()

def test_forme_order_mundo(katula_service):
    """Test l'ordre des formes pour l'univers Mundo"""
    order = katula_service._get_forme_order_for_universe('mundo')
    assert len(order) == 4
    assert order == ['carre', 'triangle', 'cercle', 'rectangle']

def test_forme_order_trigga(katula_service):
    """Test l'ordre des formes pour l'univers Trigga"""
    order = katula_service._get_forme_order_for_universe('trigga')
    assert len(order) == 16  # 4 simples + 12 composites
    # Vérifier les formes simples
    assert order[:4] == ['carre', 'triangle', 'cercle', 'rectangle']
    # Vérifier quelques formes composites
    assert 'carre-triangle' in order
    assert 'triangle-cercle' in order

def test_geometric_zone(katula_service):
    """Test la détermination des zones géométriques"""
    assert katula_service._get_geometric_zone(1, 1) == "top_left"
    assert katula_service._get_geometric_zone(4, 3) == "middle_center"
    assert katula_service._get_geometric_zone(8, 6) == "bottom_right"

def test_quadrant(katula_service):
    """Test la détermination des quadrants"""
    assert katula_service._get_quadrant(1, 1) == "Q1_top_left"
    assert katula_service._get_quadrant(3, 5) == "Q2_top_right"
    assert katula_service._get_quadrant(7, 2) == "Q3_bottom_left"
    assert katula_service._get_quadrant(8, 6) == "Q4_bottom_right"

def test_chip_compartment_creation():
    """Test la création d'un compartiment de chip"""
    comp = ChipCompartment(
        position=1,
        forme="carre",
        denomination="A1",
        petique="P1",
        tome="T1",
        granque_name="G1"
    )
    assert comp.position == 1
    assert comp.forme == "carre"
    assert comp.denomination == "A1"
    assert comp.petique == "P1"
    assert comp.tome == "T1"
    assert comp.granque_name == "G1"

@pytest.mark.integration
def test_get_chip_compartments(katula_service):
    """Test l'obtention des compartiments d'un chip (test d'intégration)"""
    result = katula_service.get_chip_compartments("mundo", 1)
    assert "universe" in result
    assert "chip_number" in result
    assert "compartments" in result
    assert result["universe"] == "mundo"
    assert result["chip_number"] == 1
    assert isinstance(result["compartments"], list)

@pytest.mark.integration
def test_get_filter_options(katula_service):
    """Test l'obtention des options de filtrage (test d'intégration)"""
    result = katula_service.get_filter_options("mundo")
    assert "universe" in result
    assert "filter_options" in result
    filter_options = result["filter_options"]
    assert "formes" in filter_options
    assert "petiques" in filter_options
    assert "tomes" in filter_options
    assert "granques" in filter_options
    assert "quadrants" in filter_options
    assert "geometric_zones" in filter_options