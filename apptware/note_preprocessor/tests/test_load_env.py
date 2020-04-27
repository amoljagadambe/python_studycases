import os

import pytest

import load_env

@pytest.mark.parametrize(
    "mysql_info,org_id,es_info",
    [
        (
            {"host": "v11", "port": "v12"},
            "org_1",
            {"host": "v11", "txt_index": "v11"},
        ),
        (
            {"host": "v21", "port": "v22"},
            "org_2",
            {"host": "v21", "txt_index": "v22"},
        ),
    ]
)
def test_load_from_file(mysql_info, org_id, es_info,tmpdir):
    p = tmpdir.join(".env")

    content = ""

    content += "mysql_info = \"host={mysql_host},port={mysql_port}\"\n".format(
        mysql_host=mysql_info.get("host"),
        mysql_port=mysql_info.get("port"),
    )
    content += "org_id = \"{org_id}\"\n".format(org_id=org_id)

    content += "es_info = \"host={es_host},txt_index={es_index}\"".format(
        es_host=es_info.get("host"),
        es_index=es_info.get("txt_index")        
    )

    p.write(content)

    omysql_info, oes_info, oorg_id = load_env.load_from_file(p)

    assert omysql_info == mysql_info
    assert oes_info == es_info
    assert oorg_id == org_id
