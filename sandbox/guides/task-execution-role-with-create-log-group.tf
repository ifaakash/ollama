# Create the IAM Policy for logging
resource "aws_iam_policy" "ecs_logging_policy" {
  name        = "${var.environment}-${var.project_name}-ecs-logging-policy"
  description = "Allows ECS to create log groups and push logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach the logging policy to your ECS role
resource "aws_iam_role_policy_attachment" "ecs_logging_policy_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_logging_policy.arn
}
