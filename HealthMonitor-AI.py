import json
import csv
import io
import re
import math
import sys
from typing import Dict, List, Union, Tuple, Any

# Set console output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Alternative approach for older Python versions
if not hasattr(sys.stdout, 'reconfigure'):
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    except AttributeError:
        pass  # If running in an environment without buffer attribute

class HealthMonitorAI:
    def __init__(self):
        self.required_fields = [
            "user_id", "current_steps", "heart_rate", 
            "ambient_temperature", "environmental_index", 
            "activity_intensity_factor"
        ]
        
    def validate_data(self, data: List[Dict[str, Any]]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate the input data according to the requirements.
        
        Args:
            data: List of user records
            
        Returns:
            Tuple containing:
                - Boolean indicating if validation passed
                - String containing validation report
                - Dictionary containing validation details
        """
        validation_results = {
            "num_users": len(data),
            "fields_check": {},
            "errors": []
        }
        
        # Check if data is empty
        if len(data) == 0:
            return False, "ERROR: No data provided.", validation_results
            
        # Check each record
        for i, record in enumerate(data):
            row_num = i + 1
            missing_fields = []
            invalid_fields = []
            
            # Check for missing fields
            for field in self.required_fields:
                if field not in record:
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"ERROR: Missing required field(s): {', '.join(missing_fields)} in row {row_num}."
                validation_results["errors"].append(error_msg)
                continue
                
            # Validate field types and values
            if not isinstance(record["user_id"], str):
                invalid_fields.append("user_id")
                
            try:
                steps = int(record["current_steps"])
                if steps <= 0:
                    invalid_fields.append("current_steps")
            except (ValueError, TypeError):
                invalid_fields.append("current_steps")
            
            try:
                heart_rate = int(record["heart_rate"])
                if heart_rate <= 0:
                    invalid_fields.append("heart_rate")
            except (ValueError, TypeError):
                invalid_fields.append("heart_rate")
                
            try:
                float(record["ambient_temperature"])
            except (ValueError, TypeError):
                invalid_fields.append("ambient_temperature")
                
            try:
                env_index = float(record["environmental_index"])
                if env_index < 0 or env_index > 100:
                    invalid_fields.append("environmental_index")
            except (ValueError, TypeError):
                invalid_fields.append("environmental_index")
                
            try:
                intensity = float(record["activity_intensity_factor"])
                if intensity <= 0:
                    invalid_fields.append("activity_intensity_factor")
            except (ValueError, TypeError):
                invalid_fields.append("activity_intensity_factor")
                
            if invalid_fields:
                error_msg = f"ERROR: Invalid value for the field(s): {', '.join(invalid_fields)} in row {row_num}. Please correct and resubmit."
                validation_results["errors"].append(error_msg)
        
        # Prepare validation check results
        for field in self.required_fields:
            if all(field in record for record in data):
                validation_results["fields_check"][field] = "present"
            else:
                validation_results["fields_check"][field] = "missing"
        
        # Check if validation passed
        validation_passed = len(validation_results["errors"]) == 0
        
        # Generate validation report
        validation_report = self._generate_validation_report(validation_results)
        
        return validation_passed, validation_report, validation_results
    
    def _generate_validation_report(self, validation_results: Dict) -> str:
        """Generate the validation report in markdown format."""
        report = "# Data Validation Report\n"
        report += "## Data Structure Check:\n"
        report += f"- Number of users: {validation_results['num_users']}\n"
        report += f"- Number of fields per record: {len(self.required_fields)}\n\n"
        
        report += "## Required Fields Check:\n"
        for field, status in validation_results["fields_check"].items():
            valid_status = "valid" if status == "present" else "invalid"
            report += f"- {field}: {valid_status}\n"
        
        report += "\n## Validation Summary:\n"
        if not validation_results["errors"]:
            report += "Data validation is successful! Would you like to proceed with analysis or provide another dataset?"
        else:
            for error in validation_results["errors"]:
                report += f"- {error}\n"
                
        return report
    
    def parse_input_data(self, data_str: str) -> List[Dict[str, Any]]:
        """
        Parse input data from either CSV or JSON format.
        
        Args:
            data_str: String containing the data in either CSV or JSON format
            
        Returns:
            List of dictionaries, each representing a user record
        """
        data_str = data_str.strip()
        
        try:
            # Try parsing as JSON
            if data_str.startswith("{"):
                data_dict = json.loads(data_str)
                if "users" in data_dict:
                    return data_dict["users"]
                return [data_dict]
            # Try parsing as CSV
            elif "," in data_str:
                csv_data = list(csv.reader(io.StringIO(data_str)))
                if len(csv_data) < 2:  # Need at least header and one data row
                    return []
                    
                headers = [h.strip() for h in csv_data[0]]
                records = []
                
                for i in range(1, len(csv_data)):
                    if len(csv_data[i]) != len(headers):
                        continue
                        
                    record = {headers[j]: csv_data[i][j] for j in range(len(headers))}
                    
                    # Convert numeric fields to appropriate types
                    for field in ["current_steps", "heart_rate"]:
                        if field in record:
                            try:
                                record[field] = int(record[field])
                            except ValueError:
                                pass
                    
                    for field in ["ambient_temperature", "environmental_index", "activity_intensity_factor"]:
                        if field in record:
                            try:
                                record[field] = float(record[field])
                            except ValueError:
                                pass
                    
                    records.append(record)
                
                return records
            else:
                return []
        except Exception:
            return []
    
    def calculate_metrics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all required metrics for a user.
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Dictionary containing all calculated metrics
        """
        results = {
            "input_data": user_data.copy(),
            "calculations": {}
        }
        
        # 1. Predicted Activity Calculation
        predicted_activity = user_data["current_steps"] * user_data["activity_intensity_factor"]
        results["calculations"]["predicted_activity"] = round(predicted_activity, 2)
        
        # 2. Heart Rate Category
        heart_rate = user_data["heart_rate"]
        if heart_rate < 60:
            heart_rate_category = "Below Optimal"
        elif 60 <= heart_rate <= 100:
            heart_rate_category = "Optimal"
        else:
            heart_rate_category = "Above Optimal"
        results["calculations"]["heart_rate_category"] = heart_rate_category
        
        # 3. Environmental Quality Category
        env_index = user_data["environmental_index"]
        if env_index >= 75:
            env_quality = "Good"
        elif env_index >= 50:
            env_quality = "Moderate"
        else:
            env_quality = "Poor"
        results["calculations"]["environmental_quality"] = env_quality
        
        # 4. Ambient Temperature Impact
        temp = user_data["ambient_temperature"]
        if 15 <= temp <= 25:
            temp_impact = "Ideal Temperature"
        elif temp < 15:
            temp_impact = "Too Cold"
        else:
            temp_impact = "Too Hot"
        results["calculations"]["temperature_impact"] = temp_impact
        
        # 5. Composite Fitness Score
        # Define factors
        heart_rate_factors = {"Optimal": 1, "Below Optimal": 0.8, "Above Optimal": 0.7}
        env_factors = {"Good": 1, "Moderate": 0.8, "Poor": 0.6}
        
        heart_rate_factor = heart_rate_factors[heart_rate_category]
        env_factor = env_factors[env_quality]
        
        # Calculate components
        normalized_activity = (predicted_activity / 10000) * 0.5
        heart_component = heart_rate_factor * 0.3
        env_component = env_factor * 0.2
        
        composite_score = normalized_activity + heart_component + env_component
        results["calculations"]["normalized_activity"] = round(normalized_activity, 2)
        results["calculations"]["heart_component"] = round(heart_component, 2)
        results["calculations"]["env_component"] = round(env_component, 2)
        results["calculations"]["composite_fitness_score"] = round(composite_score, 2)
        
        # 6. Final Recommendation
        if (composite_score >= 0.75 and 
            heart_rate_category == "Optimal" and 
            temp_impact == "Ideal Temperature"):
            recommendation = "Continue current fitness plan"
            status = "Optimal"
        else:
            recommendation = "Adjust fitness plan"
            status = "Needs Adjustment"
        
        results["calculations"]["recommendation"] = recommendation
        results["calculations"]["status"] = status
        
        return results
    
    def generate_report(self, metrics: Dict[str, Any]) -> str:
        """
        Generate the final report in markdown format.
        
        Args:
            metrics: Dictionary containing all calculated metrics
            
        Returns:
            String containing the report in markdown format
        """
        user_data = metrics["input_data"]
        calcs = metrics["calculations"]
        
        report = f"# Health Monitoring Summary\n\n"
        report += f"**User ID:** {user_data['user_id']}\n\n"
        report += "---\n\n"
        
        # Input Data section
        report += "## Input Data:\n"
        for field in self.required_fields:
            report += f"- {field}: {user_data[field]}\n"
        
        report += "\n---\n\n"
        
        # Detailed Calculations section
        report += "## Detailed Calculations:\n\n"
        
        # 1. Predicted Activity
        report += "1. Predicted Activity Calculation:\n"
        report += " - Formula: $$ \\text{Predicted Activity} = \\text{current_steps} \\times \\text{activity_intensity_factor} $$\n"
        report += " - Steps: Multiply current_steps by activity_intensity_factor.\n"
        report += f" - Calculation: {user_data['current_steps']} \\times {user_data['activity_intensity_factor']} = {calcs['predicted_activity']}\n"
        report += f" - Calculated Value: **{calcs['predicted_activity']} steps**\n\n"
        
        # 2. Heart Rate Category
        report += "2. Heart Rate Category:\n"
        report += " - IF heart_rate < 60, THEN \"Below Optimal\".\n"
        report += " - ELSE IF heart_rate between 60 and 100, THEN \"Optimal\".\n"
        report += " - ELSE, \"Above Optimal\".\n"
        report += f" - Given heart_rate = {user_data['heart_rate']}\n"
        report += f" - Result: **{calcs['heart_rate_category']}**\n\n"
        
        # 3. Environmental Quality
        report += "3. Environmental Quality Category:\n"
        report += " - IF environmental_index ≥ 75, THEN \"Good\".\n"
        report += " - ELSE IF environmental_index ≥ 50, THEN \"Moderate\".\n"
        report += " - ELSE, \"Poor\".\n"
        report += f" - Given environmental_index = {user_data['environmental_index']}\n"
        report += f" - Result: **{calcs['environmental_quality']}**\n\n"
        
        # 4. Temperature Impact
        report += "4. Ambient Temperature Impact:\n"
        report += " - IF ambient_temperature between 15 and 25, THEN \"Ideal Temperature\".\n"
        report += " - ELSE IF ambient_temperature < 15, THEN \"Too Cold\".\n"
        report += " - ELSE, \"Too Hot\".\n"
        report += f" - Given ambient_temperature = {user_data['ambient_temperature']}\n"
        report += f" - Result: **{calcs['temperature_impact']}**\n\n"
        
        # 5. Composite Fitness Score
        report += "5. Composite Fitness Score Calculation:\n"
        report += " - Formula: $$ \\text{Composite Fitness Score} = \\left(\\frac{\\text{Predicted Activity}}{10000} \\times 0.5\\right) + \\left(\\text{Heart Rate Factor} \\times 0.3\\right) + \\left(\\text{Environmental Factor} \\times 0.2\\right) $$\n"
        
        # Get factors based on categories
        heart_factor_value = {"Optimal": 1, "Below Optimal": 0.8, "Above Optimal": 0.7}[calcs['heart_rate_category']]
        env_factor_value = {"Good": 1, "Moderate": 0.8, "Poor": 0.6}[calcs['environmental_quality']]
        
        report += " - Steps:\n"
        report += f"   1. Normalized activity: ${calcs['predicted_activity']} \\div 10000 \\times 0.5 = {calcs['normalized_activity']}$\n"
        report += f"   2. Heart Rate Factor: Heart rate category is \"{calcs['heart_rate_category']}\" which gives a factor of {heart_factor_value}\n"
        report += f"      Heart component: ${heart_factor_value} \\times 0.3 = {calcs['heart_component']}$\n"
        report += f"   3. Environmental Factor: Environmental quality is \"{calcs['environmental_quality']}\" which gives a factor of {env_factor_value}\n"
        report += f"      Environmental component: ${env_factor_value} \\times 0.2 = {calcs['env_component']}$\n"
        report += f"   4. Composite Fitness Score: ${calcs['normalized_activity']} + {calcs['heart_component']} + {calcs['env_component']} = {calcs['composite_fitness_score']}$\n"
        report += f" - Calculated Value: **{calcs['composite_fitness_score']}**\n\n"
        
        report += "---\n\n"
        
        # Final Recommendation
        report += "## Final Recommendation:\n\n"
        report += f"- Recommendation: **{calcs['recommendation']}**\n"
        report += f"- Status: **{calcs['status']}**\n"
        
        return report
    
    def process_data(self, data_str: str) -> str:
        """
        Process data and generate final output.
        
        Args:
            data_str: String containing the data in either CSV or JSON format
            
        Returns:
            String containing either validation errors or the final report
        """
        # Parse input data
        data = self.parse_input_data(data_str)
        
        if not data:
            return "ERROR: Invalid data format. Please provide data in CSV or JSON format."
        
        # Validate data
        valid, validation_report, _ = self.validate_data(data)
        
        if not valid:
            return validation_report
        
        # Process each user record
        results = []
        for user_data in data:
            metrics = self.calculate_metrics(user_data)
            report = self.generate_report(metrics)
            results.append(report)
        
        # Return all reports concatenated with a separator
        return "\n\n" + "\n\n---\n\n".join(results)

def main():
    """
    Main function to handle user interaction.
    """
    monitor = HealthMonitorAI()
    sample_data = """user_id,current_steps,heart_rate,ambient_temperature,environmental_index,activity_intensity_factor
U41,7100,75,20,80,1.1
U42,8200,80,21,85,1.2
U43,9000,90,19,70,1.0
U44,10000,95,18,90,1.3
U45,7500,65,22,75,1.1
U46,8000,70,20,60,1.2
U47,9500,85,23,80,1.0
U48,8700,78,21,88,1.2
U49,9100,92,24,77,1.1
U50,9800,88,19,82,1.0"""

        
    result = monitor.process_data(sample_data)
    print("\nResult:")
    print(result)

if __name__ == "__main__":
    main()