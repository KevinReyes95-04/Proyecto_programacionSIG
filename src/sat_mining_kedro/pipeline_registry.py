from kedro.pipeline import Pipeline

from sat_mining_kedro.pipelines.data_engineering.pipeline import create_pipeline as de_pipeline
from sat_mining_kedro.pipelines.features.pipeline import create_pipeline as feat_pipeline
from sat_mining_kedro.pipelines.train_binary_rf.pipeline import create_pipeline as binary_pipeline
from sat_mining_kedro.pipelines.train_multiclass_rf.pipeline import create_pipeline as multi_pipeline
from sat_mining_kedro.pipelines.evaluate.pipeline import create_pipeline as eval_pipeline
from sat_mining_kedro.pipelines.predict.pipeline import create_pipeline as pred_pipeline


def register_pipelines() -> dict[str, Pipeline]:
    data_engineering = de_pipeline()
    features = feat_pipeline()
    train_binary_rf = binary_pipeline()
    train_multiclass_rf = multi_pipeline()
    evaluate = eval_pipeline()
    predict = pred_pipeline()

    return {
        "data_engineering": data_engineering,
        "features": features,
        "train_binary_rf": train_binary_rf,
        "train_multiclass_rf": train_multiclass_rf,
        "evaluate": evaluate,
        "predict": predict,
        "__default__": data_engineering + features + train_binary_rf + train_multiclass_rf + evaluate + predict,
    }
