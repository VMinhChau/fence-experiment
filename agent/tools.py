"""
Banking tools for the FENCE experiment.

The tools receive a shared AuthorityManager from the application runtime.

This module does NOT own the authority state.
"""

from authority.manager import AuthorityManager


AGENT_ID = "fence_agent"
AUTHORITY_ID = "T"


# ============================================================
# Banking data
# ============================================================

CUSTOMER_DATABASE = {
    "C001": {
        "customer_id": "C001",
        "risk_level": "HIGH",
        "country": "VN",
        "transaction_count_30d": 47,
        "total_transaction_value": 1_850_000_000,
        "suspicious_transaction_count": 3,
    },
    "C002": {
        "customer_id": "C002",
        "risk_level": "LOW",
        "country": "VN",
        "transaction_count_30d": 12,
        "total_transaction_value": 85_000_000,
        "suspicious_transaction_count": 0,
    },
}


ALERT_DATABASE = {
    "C001": {
        "customer_id": "C001",
        "alert_status": "OPEN",
        "alert_type": "UNUSUAL_TRANSACTION_PATTERN",
        "severity": "HIGH",
    },
    "C002": {
        "customer_id": "C002",
        "alert_status": "NONE",
        "alert_type": None,
        "severity": None,
    },
}


# ============================================================
# Tool factory
# ============================================================

def create_banking_tools(authority_manager: AuthorityManager):
    """
    Create banking tools bound to the shared AuthorityManager.

    The AuthorityManager is owned by the application runtime,
    not by this module.
    """

    def get_customer_risk_profile(customer_id: str) -> dict:
        """
        Retrieve a customer's risk profile.

        Authorization is checked before accessing the data.
        """

        resource = f"customer:{customer_id}"

        allowed = authority_manager.check(
            agent_id=AGENT_ID,
            resource=resource,
            action="read_risk_profile",
        )

        if not allowed:
            return {
                "status": "DENIED",
                "reason": "Agent does not have active authority",
                "customer_id": customer_id,
            }

        return CUSTOMER_DATABASE.get(
            customer_id,
            {
                "customer_id": customer_id,
                "risk_level": "UNKNOWN",
                "message": "Customer not found",
            },
        )

    def check_transaction_alert(customer_id: str) -> dict:
        """
        Retrieve AML alert information.

        This tool has its own authorization requirement.
        """

        resource = f"customer:{customer_id}"

        allowed = authority_manager.check(
            agent_id=AGENT_ID,
            resource=resource,
            action="read_transaction_alert",
        )

        if not allowed:
            return {
                "status": "DENIED",
                "reason": "Agent does not have active authority",
                "customer_id": customer_id,
            }

        return ALERT_DATABASE.get(
            customer_id,
            {
                "customer_id": customer_id,
                "alert_status": "UNKNOWN",
            },
        )

    return [
        get_customer_risk_profile,
        check_transaction_alert,
    ]