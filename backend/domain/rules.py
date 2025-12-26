from .enums import Decision


class DecisionRules:

    @staticmethod
    def decide(confidence: float) -> Decision:
        if confidence >= 0.8:
            return Decision.ACCEPT
        elif confidence >= 0.5:
            return Decision.REVIEW
        else:
            return Decision.REJECT
