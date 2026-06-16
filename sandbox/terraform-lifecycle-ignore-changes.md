# Terraform Lifecycle `ignore_changes`

In Terraform, you can use the `lifecycle` block with the `ignore_changes` argument to instruct Terraform to ignore manual changes or changes made by external processes to specific attributes of a resource. This prevents Terraform from attempting to revert those changes during the next `terraform apply`.

Here is the basic syntax:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "MyInstance"
  }

  # This is the lifecycle block
  lifecycle {
    ignore_changes = [
      # Ignore changes to the 'tags' attribute entirely
      tags,
    ]
  }
}
```

## Different ways to use `ignore_changes`:

### 1. Ignore specific attributes
List the specific arguments you want Terraform to ignore if they drift from the state file.

```hcl
  lifecycle {
    ignore_changes = [
      ami,
      instance_type,
    ]
  }
```

### 2. Ignore specific keys in a map (like `tags`)
If you only want to ignore changes to a specific tag (e.g., a tag managed by an external auto-tagging system), but still want Terraform to manage other tags:

```hcl
  lifecycle {
    ignore_changes = [
      tags["Environment"],
      tags["AutoScalingGroup"],
    ]
  }
```

### 3. Ignore all changes
If you want Terraform to create the resource initially but never update it again, even if you change the configuration or if the actual infrastructure changes, use the `all` keyword:

```hcl
  lifecycle {
    ignore_changes = all
  }
```

## Common Use Cases:
*   **Tags:** When another tool or AWS process adds/modifies tags outside of Terraform (e.g., ASG dynamic tags).
*   **Desired Capacity / Instance Counts:** When using Auto Scaling Groups or ECS Services where the actual running count is managed dynamically by autoscaling rules, not strictly by your static Terraform code.
*   **Database Passwords:** To prevent Terraform from attempting to reset a database password that a user or automated system has rotated since the database was initially created.
