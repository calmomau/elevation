# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 B-Open Solutions srl - http://bopen.eu
#

# python 2 support via python-future
from __future__ import absolute_import, unicode_literals

import subprocess

from elevation import datasource


def test_srtm3_tile_ilonlat():
    # values from http://srtm.csi.cgiar.org/SELECTION/inputCoord.asp
    assert datasource.srtm3_tile_ilonlat(-177.5, 52.5) == (1, 2)
    assert datasource.srtm3_tile_ilonlat(177.5, -47.5) == (72, 22)
    assert datasource.srtm3_tile_ilonlat(10.1, 44.9) == (39, 4)
    assert datasource.srtm3_tile_ilonlat(14.9, 44.9) == (39, 4)
    assert datasource.srtm3_tile_ilonlat(10.1, 40.1) == (39, 4)
    assert datasource.srtm3_tile_ilonlat(14.9, 40.1) == (39, 4)


def test_srtm3_tiles_names():
    assert next(datasource.srtm3_tiles_names(10.1, 44.9, 10.1, 44.9)).endswith('srtm_39_04.tif')
    assert len(list(datasource.srtm3_tiles_names(9.9, 39.1, 15.1, 45.1))) == 9


def test_ensure_tiles(mocker):
    with mocker.patch('subprocess.check_call'):
        cmd = datasource.ensure_tiles('/tmp', ['a', 'b'], make_flags='-s')
    assert cmd == 'make -C /tmp -s download ENSURE_TILES="a b"'
    subprocess.check_call.assert_called_once_with(cmd, shell=True)


def test_do_clip(mocker):
    bounds = (1, 5, 2, 6)
    with mocker.patch('subprocess.check_call'):
        cmd = datasource.do_clip(path='/tmp', bounds=bounds, output='/out.tif', make_flags='-s')
    assert cmd == 'make -C /tmp -s clip OUTPUT="/out.tif" PROJWIN="1 6 2 5"'
    subprocess.check_call.assert_called_once_with(cmd, shell=True)


def test_seed(mocker, tmpdir):
    root = tmpdir.join('root')
    bounds = (13.1, 43.1, 13.9, 43.9)
    with mocker.patch('subprocess.check_call'):
        datasource.seed(cache_dir=str(root), product='SRTMGL1', bounds=bounds)
    assert len(root.listdir()) == 1
    datasource_root = root.listdir()[0]
    expected_cmd = 'make -C %s  download ENSURE_TILES="N43E013.tif"' % datasource_root
    subprocess.check_call.assert_any_call(expected_cmd, shell=True)


def test_clip(mocker, tmpdir):
    root = tmpdir.join('root')
    bounds = (13.1, 43.1, 14.9, 44.9)
    with mocker.patch('subprocess.check_call'):
        datasource.clip(cache_dir=str(root), product='SRTMGL1', bounds=bounds, output='out.tif')
    assert len(root.listdir()) == 1
    datasource_root = root.listdir()[0]
    expected_cmd = 'make -C %s  clip OUTPUT="out.tif" PROJWIN="13.1 44.9 14.9 43.1"' % datasource_root
    subprocess.check_call.assert_any_call(expected_cmd, shell=True)


def test_clean(mocker, tmpdir):
    root = tmpdir.join('root')
    with mocker.patch('subprocess.check_call'):
        datasource.clean(cache_dir=str(root), product='SRTMGL1')
    assert len(root.listdir()) == 1
    datasource_root = root.listdir()[0]
    subprocess.check_call.assert_any_call('make -C %s  clean ' % datasource_root, shell=True)
