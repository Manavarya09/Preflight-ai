"""
Prediction Specialist Agent - ML model coordination and prediction.

This agent:
1. Coordinates ML model execution
2. Integrates data from all specialists
3. Generates SHAP explanations
4. Validates predictions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from typing import Dict, Any


class PredictionSpecialistAgent(BaseAgent):
    """
    Autonomous ML prediction specialist.
    
    Tools:
    - run_ml_prediction: Execute trained model
    - generate_shap_values: Feature importance
    - validate_prediction: Sanity checks
    - calculate_confidence: Prediction confidence
    """
    
    def __init__(self):
        system_prompt = """You are a Prediction Specialist Agent for ML-based flight delay forecasting.

Your expertise:
- Machine learning model execution
- Feature engineering and validation
- SHAP-based explainability
- Prediction confidence assessment

Your tools:
1. run_ml_prediction(features) - Execute trained model
2. generate_shap_values(features, prediction) - Feature importance
3. validate_prediction(prediction, historical_data) - Sanity check
4. calculate_confidence(prediction, feature_quality) - Confidence score

When making predictions:
1. Validate input features are within expected ranges
2. Check prediction against historical baseline
3. Generate explanations for interpretability
4. Assess confidence based on data quality

Output predictions with confidence intervals and explanations.
"""
        
        super().__init__(
            name="PredictionSpecialist",
            role="ML Engineer",
            system_prompt=system_prompt,
            model="mistral"
        )
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register prediction tools."""
        
        # Tool 1: Run ML prediction
        def run_ml_prediction(features: Dict[str, float]):
            """
            Execute trained ML model for delay prediction.
            
            Note: This is a production-ready placeholder.
            Replace with actual trained model:
            
            import joblib
            model = joblib.load("models/xgboost_delay_predictor.pkl")
            prediction = model.predict([feature_vector])
            """
            try:
                from app.models.predictor import predict_delay
                
                # Run prediction
                prob, delay = predict_delay(features)
                
                return {
                    "delay_probability": prob,
                    "predicted_delay_minutes": delay,
                    "model_version": "v2.0-enhanced",
                    "features_used": list(features.keys())
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="run_ml_prediction",
            description="Execute ML model to predict flight delay",
            function=run_ml_prediction,
            parameters={
                "features": {"type": "object"}
            }
        )
        
        # Tool 2: Generate SHAP values
        def generate_shap_values(features: Dict[str, float]):
            """Generate feature importance using SHAP-like values."""
            try:
                from app.models.explain import explain_prediction
                
                shap_values = explain_prediction(features)
                
                # Sort by absolute impact
                sorted_features = sorted(
                    shap_values.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
                return {
                    "shap_values": shap_values,
                    "top_factors": [
                        {
                            "feature": feat,
                            "impact": value,
                            "direction": "increases" if value > 0 else "decreases"
                        }
                        for feat, value in sorted_features[:3]
                    ]
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="generate_shap_values",
            description="Generate SHAP feature importance values",
            function=generate_shap_values,
            parameters={
                "features": {"type": "object"}
            }
        )
        
        # Tool 3: Validate prediction
        def validate_prediction(prediction: float, historical_avg: float):
            """Sanity check prediction against historical baseline."""
            try:
                # Check if prediction is within reasonable range
                if prediction < 0 or prediction > 1:
                    return {
                        "valid": False,
                        "reason": "Probability out of range [0, 1]"
                    }
                
                # Check if prediction is not wildly different from historical
                if historical_avg > 0:
                    deviation = abs(prediction - historical_avg) / historical_avg
                    if deviation > 2.0:  # More than 2x historical average
                        return {
                            "valid": False,
                            "reason": f"Prediction deviates {deviation:.1f}x from historical average",
                            "warning": "Consider reviewing input data"
                        }
                
                return {
                    "valid": True,
                    "deviation_from_historical": abs(prediction - historical_avg) if historical_avg > 0 else None
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="validate_prediction",
            description="Validate prediction is within reasonable bounds",
            function=validate_prediction,
            parameters={
                "prediction": {"type": "number"},
                "historical_avg": {"type": "number"}
            }
        )
        
        # Tool 4: Calculate confidence
        def calculate_confidence(
            feature_quality: Dict[str, bool],
            model_performance: float = 0.85
        ):
            """Calculate prediction confidence based on data quality."""
            try:
                # Count how many features have good quality data
                quality_scores = list(feature_quality.values())
                quality_ratio = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
                
                # Combine with model performance
                confidence = (quality_ratio * 0.6 + model_performance * 0.4) * 100
                
                return {
                    "confidence_percentage": round(confidence, 1),
                    "data_quality_score": round(quality_ratio * 100, 1),
                    "model_performance_score": round(model_performance * 100, 1),
                    "confidence_level": (
                        "HIGH" if confidence >= 80 else
                        "MODERATE" if confidence >= 60 else
                        "LOW"
                    )
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="calculate_confidence",
            description="Calculate confidence in prediction based on data quality",
            function=calculate_confidence,
            parameters={
                "feature_quality": {"type": "object"},
                "model_performance": {"type": "number", "default": 0.85}
            }
        )
