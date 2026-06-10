from fraud_detection_pipeline.main import run_pipeline


def test_run_pipeline_output(capsys):
    run_pipeline()
    captured = capsys.readouterr()
    assert "Fraud detection pipeline started" in captured.out
