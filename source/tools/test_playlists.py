"""Behavioral regression tests for multi-source playlists and safe compilation."""
import copy
import json
from pathlib import Path
import pytest
import compile_deck as deck


def example():
    return deck.load_playlist_file(deck.PRESENTATIONS / 'playlists/mixed-example.json')


def test_mixed_sources_bundles_order_and_notes():
    units = deck.resolve_playlist(example())
    assert [u['_source'] for u in units] == ['common:opening#opening', 'workshop:shared-plan#choose', 'workshop:shared-plan#commit', 'metronomics:13-rule#13-rule']
    assert units[1]['artifact'] == 'shared-plan-example'
    assert units[1]['notes'] == ['Invite each participant to describe the outcome.']


def test_repeated_reference_selection_and_override_leave_source_unchanged():
    p = example()
    p['units'] = [{'id':'workshop:shared-plan','slides':['commit','choose']}, {'id':'workshop:shared-plan','slides':['commit'],'override':{'headline':'A local variation.'}}]
    units=deck.resolve_playlist(p)
    assert [u['id'] for u in units] == ['commit','choose','commit']
    assert units[-1]['headline']=='A local variation.'
    assert deck.resolve_playlist(example())[2]['headline']=='Leave with an owner and a next step.'
    rendered=deck.render_deck(p, units)
    assert all(f'id="slide-{n}"' in rendered for n in range(1,4))


@pytest.mark.parametrize('entry', ['unknown:opening','workshop:../escape',{'id':'workshop:shared-plan','slides':['missing']},{'id':'workshop:shared-plan','override':{'_root':'/'}}])
def test_invalid_refs_fail_closed(entry):
    p=example();p['units']=[entry]
    with pytest.raises(deck.CompileError):deck.resolve_playlist(p)


def test_assets_bundled_and_provenance_portable(tmp_path):
    out=deck.compile_playlist('mixed-example',tmp_path/'output',deck.PRESENTATIONS/'playlists/mixed-example.json')
    manifest=json.loads((out/'manifest.json').read_text())
    assert len(manifest['sources'])==4
    assert all(len(s['sha256'])==64 for s in manifest['sources'])
    assert '/Users/' not in (out/'manifest.json').read_text()
    import re
    for src in re.findall(r'<img[^>]*src="\./([^"]+)"',(out/'index.html').read_text()):
        assert (out/src).is_file()
    assert 'Invite each participant' in (out/'index.html').read_text()


def test_invalid_compile_preserves_previous_output(tmp_path):
    out=deck.compile_playlist('kickoff-sample',tmp_path/'out')
    before=(out/'index.html').read_bytes()
    p=example();p['units']=['missing:unit'];p.pop('_base')
    source=tmp_path/'bad.json';source.write_text(json.dumps(p))
    with pytest.raises(deck.CompileError):deck.compile_playlist('bad',out,source)
    assert (out/'index.html').read_bytes()==before


def test_refuse_arbitrary_directory_even_with_foreign_manifest(tmp_path):
    out=tmp_path/'personal';out.mkdir();(out/'manifest.json').write_text('{}');(out/'keep.txt').write_text('keep')
    with pytest.raises(deck.CompileError):deck.compile_playlist('kickoff-sample',out)
    assert (out/'keep.txt').read_text()=='keep'


def test_missing_artwork_and_traversal_fail(tmp_path):
    u=deck.resolve_playlist(example())[:1]
    for src in ['../../private.png','assets/missing.png']:
        unit=copy.deepcopy(u);unit[0]['artwork']['src']=src
        with pytest.raises(deck.CompileError):deck.prepare_artwork(unit,tmp_path)


def test_populated_title_requires_artwork():
    with pytest.raises(deck.CompileError,match='requires artwork'):
        deck.render_slide({'id':'title','title':'Title','headline':'Title','layout':'title'},1)


def test_compilation_is_reproducible(tmp_path):
    first=deck.compile_playlist('kickoff-sample',tmp_path/'first')
    second=deck.compile_playlist('kickoff-sample',tmp_path/'second')
    assert {p.relative_to(first):p.read_bytes() for p in first.rglob('*') if p.is_file()} == {p.relative_to(second):p.read_bytes() for p in second.rglob('*') if p.is_file()}


def test_output_symlink_preserves_target(tmp_path):
    target=deck.compile_playlist('kickoff-sample',tmp_path/'target')
    before=(target/'index.html').read_bytes()
    link=tmp_path/'alias';link.symlink_to(target, target_is_directory=True)
    with pytest.raises(deck.CompileError,match='symlink'):deck.compile_playlist('kickoff-sample',link)
    assert (target/'index.html').read_bytes()==before


def test_connected_causal_sequence_rejects_four_panels():
    with pytest.raises(deck.CompileError,match='at most three'):
        deck.render_slide({'id':'flow','layout':'comp-causal','panels':[{'heading':'Step'}]*4},1)


def test_legacy_decision_roles_preserved():
    rendered=deck.render_slide({'id':'decision','layout':'comp-decision','body':['Do it','Leave it']},1)
    assert 'mark-action' in rendered and 'mark-gap' in rendered
    assert '>Action<' in rendered and '>Gap<' in rendered


def test_missing_headline_rejected(tmp_path):
    (tmp_path/'bad.json').write_text(json.dumps({'id':'bad','layout':'comp-rule','title':'Missing headline'}))
    with pytest.raises(deck.CompileError,match='requires string'):
        deck.resolve_playlist({'sources':{'test':str(tmp_path)},'units':['test:bad']})


def test_six_questions_hover_matches_the_priorities_slide():
    """Every "six questions" hover repeats the selection slide's headings word for word."""
    lib = Path(__file__).resolve().parent.parent / "libraries" / "kickoff"
    quality = next(s for s in json.loads((lib / "priorities.json").read_text())["slides"] if s["id"] == "quality")
    headings = [p["heading"] for p in quality["panels"]]
    assert len(headings) == 6
    found = 0
    for path in lib.glob("*.json"):
        for slide in json.loads(path.read_text()).get("slides", []):
            for term in slide.get("terms", []):
                if term["term"] == "six questions":
                    found += 1
                    assert term["tip"] == headings, f"{path.name}#{slide['id']}"
    assert found >= 2
