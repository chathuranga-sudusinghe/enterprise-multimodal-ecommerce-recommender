from ecommerce_recommender.models.abo_clip_similarity import DEFAULT_CLIP_MODEL_NAME
from scripts.run_abo_clip_similarity import parse_args


def test_parse_args_keeps_online_loading_as_default() -> None:
    args = parse_args([])

    assert args.model_name == DEFAULT_CLIP_MODEL_NAME
    assert args.local_files_only is False


def test_parse_args_enables_local_cache_only_loading() -> None:
    args = parse_args(["--model-name", "local/clip", "--local-files-only"])

    assert args.model_name == "local/clip"
    assert args.local_files_only is True
