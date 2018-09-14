#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `chariot_privacy_engine` package."""

import falcon
from falcon import testing
import json
import pytest

from chariot_privacy_engine.app import app


@pytest.fixture
def client():
    return testing.TestClient(app)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_list_images(client):
    doc = {
        'status': 0
    }

    response = client.simulate_get('/things')
    result_doc = json.loads(response.content)

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK
