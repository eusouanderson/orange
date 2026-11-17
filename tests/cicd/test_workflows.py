"""Testes automatizados para validação da GitHub Action e Workflows de CI/CD."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_action_yml_structure():
    action_file = ROOT / 'action.yml'
    assert action_file.exists()

    data = yaml.safe_load(action_file.read_text(encoding='utf-8'))
    assert data['name'] == 'Orange Framework Build'
    assert data['runs']['using'] == 'composite'

    inputs = data['inputs']
    expected_inputs = [
        'source',
        'output',
        'profile',
        'compile-all',
        'python-version',
        'platform',
        'orange-version',
        'config-file',
        'cache',
        'upload-artifact',
    ]
    for inp in expected_inputs:
        assert inp in inputs, f'Input ausente em action.yml: {inp}'

    outputs = data['outputs']
    assert 'executable-path' in outputs
    assert 'build-status' in outputs


def test_ci_workflow_structure():
    ci_file = ROOT / '.github' / 'workflows' / 'ci.yml'
    assert ci_file.exists()

    data = yaml.safe_load(ci_file.read_text(encoding='utf-8'))
    assert 'lint' in data['jobs']
    assert 'test-matrix' in data['jobs']
    matrix = data['jobs']['test-matrix']['strategy']['matrix']
    assert '3.10' in matrix['python-version']
    assert '3.13' in matrix['python-version']


def test_tests_workflow_matrix():
    tests_file = ROOT / '.github' / 'workflows' / 'tests.yml'
    assert tests_file.exists()

    data = yaml.safe_load(tests_file.read_text(encoding='utf-8'))
    matrix = data['jobs']['test-platforms']['strategy']['matrix']
    expected_os = ['ubuntu-latest', 'windows-latest', 'macos-latest']
    for os_target in expected_os:
        assert os_target in matrix['os']


def test_build_workflow_structure():
    build_file = ROOT / '.github' / 'workflows' / 'build.yml'
    assert build_file.exists()

    data = yaml.safe_load(build_file.read_text(encoding='utf-8'))
    assert 'build-matrix' in data['jobs']
    matrix = data['jobs']['build-matrix']['strategy']['matrix']
    assert 'ubuntu-latest' in matrix['os']
    assert 'windows-latest' in matrix['os']
    assert 'macos-latest' in matrix['os']


def test_release_workflow_triggers_and_permissions():
    release_file = ROOT / '.github' / 'workflows' / 'release.yml'
    assert release_file.exists()

    data = yaml.safe_load(release_file.read_text(encoding='utf-8'))
    on_clause = data.get('on') or data.get(True)
    assert 'v*' in on_clause['push']['tags']
    assert data['permissions']['contents'] == 'write'
    assert 'build-release-artifacts' in data['jobs']
    assert 'create-github-release' in data['jobs']


def test_publish_pypi_workflow_oidc():
    publish_file = ROOT / '.github' / 'workflows' / 'publish-pypi.yml'
    assert publish_file.exists()

    data = yaml.safe_load(publish_file.read_text(encoding='utf-8'))
    assert data['permissions']['id-token'] == 'write'
    assert 'build-and-publish' in data['jobs']


def test_reusable_workflow_call():
    reusable_file = ROOT / '.github' / 'workflows' / 'reusable-build.yml'
    assert reusable_file.exists()

    data = yaml.safe_load(reusable_file.read_text(encoding='utf-8'))
    on_clause = data.get('on') or data.get(True)
    assert 'workflow_call' in on_clause
    inputs = on_clause['workflow_call']['inputs']
    assert 'source' in inputs
    assert 'profile' in inputs
    assert 'compile-all' in inputs
