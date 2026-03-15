#!/usr/bin/env bash
# TeacherOS - Add Teacher Workspace Script (Administrator)
# Path: setup/add-teacher.sh
# Purpose: David (Administrator) creates workspace and permissions for new teachers
# Usage: bash setup/add-teacher.sh
# Note: For administrators only

set -e

# ============================================================
# Colors and symbols
# ============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CHECK="✓"
WARN="⚠"
ERROR="✗"
INFO="ℹ"

# ============================================================
# Helper functions
# ============================================================

print_banner() {
  echo ""
  echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC}  TeacherOS - Add Teacher Workspace                 ${BLUE}║${NC}"
  echo -e "${BLUE}║${NC}  Administrator Tool (David Only)                   ${BLUE}║${NC}"
  echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
  echo ""
}

print_section() {
  echo ""
  echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}──────────────────────────────────────────────────────${NC}"
}

print_success() {
  echo -e "${GREEN}${CHECK} $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}${WARN} $1${NC}"
}

print_error() {
  echo -e "${RED}${ERROR} $1${NC}"
}

print_info() {
  echo -e "${BLUE}${INFO} $1${NC}"
}

# Prompt for input with validation (required)
get_input() {
  local prompt_msg="$1"
  local input_value=""

  while [ -z "$input_value" ]; do
    echo -ne "${CYAN}${prompt_msg}${NC}: "
    read -r input_value

    if [ -z "$input_value" ]; then
      print_error "This field cannot be empty"
    fi
  done

  echo "$input_value"
}

# Prompt for optional input (can be empty)
get_optional_input() {
  local prompt_msg="$1"
  local default_value="$2"
  local input_value

  echo -ne "${CYAN}${prompt_msg}${NC}"
  if [ -n "$default_value" ]; then
    echo -ne " (default: $default_value)${NC}: "
  else
    echo -ne " (optional, press Enter to skip)${NC}: "
  fi

  read -r input_value

  if [ -z "$input_value" ]; then
    echo "$default_value"
  else
    echo "$input_value"
  fi
}

# ============================================================
# Admin check
# ============================================================

check_admin() {
  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  ACL_FILE="$REPO_ROOT/ai-core/acl.yaml"

  if [ ! -f "$ACL_FILE" ]; then
    print_error "Cannot find ai-core/acl.yaml"
    exit 1
  fi

  print_info "Confirming administrator access..."
  print_warning "This script should be run by David (administrator)"
  echo ""
  echo -e "${YELLOW}If you are David, please continue.${NC}"
  echo -ne "${YELLOW}Confirm you are an administrator? (yes/no): ${NC}"
  read -r confirm

  if [ "$confirm" != "yes" ]; then
    print_error "Operation cancelled. This script is for administrators only."
    exit 1
  fi

  echo ""
}

# ============================================================
# Collect teacher information
# ============================================================

collect_teacher_info() {
  print_section "Step 1: Enter teacher information"

  echo ""
  print_info "Required: name, email, GitHub username"
  print_info "Optional: class code, subject (teacher can add these later)"
  echo ""

  # --- Required fields (identity) ---
  TEACHER_NAME=$(get_input "Teacher name (Traditional Chinese)")
  EMAIL=$(get_input "Email (must match teacher's environment.env USER_EMAIL)")
  GITHUB_USERNAME=$(get_input "GitHub username")

  # --- Optional fields (class/subject) ---
  echo ""
  print_info "Class and subject are optional. Teacher can create these later in their workspace."
  CLASS_CODE=$(get_optional_input "Class code (example: 4c, 9c)" "")
  SUBJECT=$(get_optional_input "Primary subject (example: English, Taiwanese)" "")

  echo ""
  print_info "Generating workspace folder name..."
  # Naming convention: Teacher_{RealName}
  WORKSPACE_FOLDER="Teacher_${TEACHER_NAME}"
  print_info "Workspace folder: $WORKSPACE_FOLDER"
  TEACHER_ID=$(get_optional_input "Workspace folder name" "$WORKSPACE_FOLDER")

  echo ""
}

# ============================================================
# Confirm information
# ============================================================

confirm_info() {
  echo ""
  print_section "Step 2: Confirm information"

  echo ""
  echo -e "${CYAN}Ready to create workspace for:${NC}"
  echo ""
  echo "  Teacher name:     $TEACHER_NAME"
  echo "  Email:            $EMAIL"
  echo "  GitHub username:  $GITHUB_USERNAME"
  if [ -n "$CLASS_CODE" ]; then
    echo "  Class code:       $CLASS_CODE"
  else
    echo "  Class code:       (none, teacher will add later)"
  fi
  if [ -n "$SUBJECT" ]; then
    echo "  Primary subject:  $SUBJECT"
  else
    echo "  Primary subject:  (none, teacher will add later)"
  fi
  echo "  Teacher ID:       $TEACHER_ID"
  echo ""

  echo -ne "${YELLOW}Is this information correct? (yes/no): ${NC}"
  read -r confirm

  if [ "$confirm" != "yes" ]; then
    print_error "Operation cancelled"
    exit 1
  fi

  echo ""
}

# ============================================================
# Create workspace directory structure
# ============================================================

create_workspace() {
  print_section "Step 3: Create workspace"

  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  WORKSPACE_DIR="$REPO_ROOT/workspaces/Working_Member/$TEACHER_ID"
  TEMPLATE_DIR="$REPO_ROOT/workspaces/_template"

  # Ensure Working_Member directory exists
  mkdir -p "$REPO_ROOT/workspaces/Working_Member"

  # Check if directory already exists
  if [ -d "$WORKSPACE_DIR" ]; then
    print_error "Workspace directory $WORKSPACE_DIR already exists"
    exit 1
  fi

  print_info "Creating workspace directory: $WORKSPACE_DIR"
  mkdir -p "$WORKSPACE_DIR"
  print_success "Directory created"

  # Copy template files
  print_info "Copying template files..."

  # teacheros-personal.yaml
  if [ -f "$TEMPLATE_DIR/teacheros-personal.yaml" ]; then
    cp "$TEMPLATE_DIR/teacheros-personal.yaml" "$WORKSPACE_DIR/teacheros-personal.yaml"
    # 自動填入 google_accounts 區塊的 email（使用教師提供的 EMAIL）
    sed -i.bak "s/{USER_EMAIL}/$EMAIL/g" "$WORKSPACE_DIR/teacheros-personal.yaml"
    rm -f "$WORKSPACE_DIR/teacheros-personal.yaml.bak"
    print_success "teacheros-personal.yaml copied, google_accounts filled with $EMAIL"
  else
    print_warning "teacheros-personal.yaml template not found — teacher must create manually"
  fi

  if [ -f "$TEMPLATE_DIR/README.md" ]; then
    cp "$TEMPLATE_DIR/README.md" "$WORKSPACE_DIR/README.md"
    print_success "README.md copied"
  fi

  # Create skills directory for personal skills
  mkdir -p "$WORKSPACE_DIR/skills"
  print_success "skills/ directory created"

  # Create workspace.yaml
  create_workspace_yaml
}

create_workspace_yaml() {
  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  WORKSPACE_DIR="$REPO_ROOT/workspaces/Working_Member/$TEACHER_ID"
  WORKSPACE_YAML="$WORKSPACE_DIR/workspace.yaml"

  print_info "Creating workspace.yaml..."

  cat > "$WORKSPACE_YAML" << 'EOF'
# TeacherOS - Teacher Workspace Configuration
# Path: workspaces/Working_Member/{TEACHER_ID}/workspace.yaml

teacher:
  name: {TEACHER_NAME}
  email: {EMAIL}
  github_username: {GITHUB_USERNAME}
  teacher_id: {TEACHER_ID}

teaching:
  class_code: {CLASS_CODE}
  primary_subject: {SUBJECT}

workspace:
  path: workspaces/Working_Member/{TEACHER_ID}/
  created_at: {TIMESTAMP}
  status: active
EOF

  # Replace placeholders
  sed -i.bak "s/{TEACHER_NAME}/$TEACHER_NAME/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{EMAIL}/$EMAIL/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{GITHUB_USERNAME}/$GITHUB_USERNAME/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{TEACHER_ID}/$TEACHER_ID/g" "$WORKSPACE_YAML"
  if [ -n "$CLASS_CODE" ]; then
    sed -i.bak "s/{CLASS_CODE}/$CLASS_CODE/g" "$WORKSPACE_YAML"
  else
    sed -i.bak "s/{CLASS_CODE}/(not yet assigned)/g" "$WORKSPACE_YAML"
  fi
  if [ -n "$SUBJECT" ]; then
    sed -i.bak "s/{SUBJECT}/$SUBJECT/g" "$WORKSPACE_YAML"
  else
    sed -i.bak "s/{SUBJECT}/(not yet assigned)/g" "$WORKSPACE_YAML"
  fi
  sed -i.bak "s/{TIMESTAMP}/$(date -u +"%Y-%m-%d %H:%M:%S UTC")/g" "$WORKSPACE_YAML"
  rm -f "$WORKSPACE_YAML.bak"

  print_success "workspace.yaml created"
}

# ============================================================
# Update acl.yaml
# ============================================================

update_acl() {
  print_section "Step 4: Update permissions (acl.yaml)"

  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  ACL_FILE="$REPO_ROOT/ai-core/acl.yaml"

  print_info "Preparing to update ai-core/acl.yaml..."

  if [ ! -f "$ACL_FILE" ]; then
    print_error "ai-core/acl.yaml does not exist"
    exit 1
  fi

  # Create new teacher entry
  local new_entry="    - name: $TEACHER_NAME
      email: $EMAIL
      github_username: $GITHUB_USERNAME
      workspace: workspaces/Working_Member/$TEACHER_ID/
      allowed_paths:
        - workspaces/Working_Member/$TEACHER_ID/
      blocked_paths:
        - ai-core/
        - setup/
        - .github/
        - publish/build.sh"

  # Use awk to insert after "  teachers:" line
  awk "/^  teachers:/{print; print \"$new_entry\"; next} 1" "$ACL_FILE" > "$ACL_FILE.tmp"
  mv "$ACL_FILE.tmp" "$ACL_FILE"

  print_success "acl.yaml updated"
}

# ============================================================
# Create class folder (only if class code was provided)
# ============================================================

create_class_folder() {
  if [ -z "$CLASS_CODE" ]; then
    print_section "Step 5: Create class folder — skipped (no class code)"
    print_info "Teacher can create class folders later in their workspace."
    return
  fi

  print_section "Step 5: Create class folder"

  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  WORKSPACE_DIR="$REPO_ROOT/workspaces/Working_Member/$TEACHER_ID"
  CLASS_DIR="$WORKSPACE_DIR/projects/class-$CLASS_CODE"

  print_info "Creating class folder: projects/class-$CLASS_CODE/"

  mkdir -p "$CLASS_DIR"
  print_success "Class folder created"

  # Create basic project.yaml if it doesn't exist elsewhere
  if [ ! -f "$CLASS_DIR/project.yaml" ]; then
    cat > "$CLASS_DIR/project.yaml" << EOF
# TeacherOS - Class Project Configuration
# Path: workspaces/$TEACHER_ID/projects/class-$CLASS_CODE/project.yaml

class:
  code: $CLASS_CODE
  subject: $SUBJECT
  teacher_id: $TEACHER_ID

status:
  created_at: $(date -u +"%Y-%m-%d")
  last_updated: $(date -u +"%Y-%m-%d")
EOF
    print_success "project.yaml created"
  fi

  echo ""
}

# ============================================================
# Create teacher's personal branch
# ============================================================

create_teacher_branch() {
  print_section "Step 6: Create teacher branch"

  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  BRANCH_NAME="workspace/$TEACHER_ID"

  print_info "Creating branch: $BRANCH_NAME"

  cd "$REPO_ROOT"

  # Create and push the branch
  git checkout -b "$BRANCH_NAME"
  git push -u origin "$BRANCH_NAME"

  # Switch back to main
  git checkout main

  print_success "Branch '$BRANCH_NAME' created and pushed to GitHub"
  echo ""
  print_info "Teacher will automatically work on this branch after clone + quick-start"
}

# ============================================================
# Print summary with self-check
# ============================================================

print_summary() {
  print_section "Step 7: Setup Complete"

  BRANCH_NAME="workspace/$TEACHER_ID"

  echo ""
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║${NC}  Teacher workspace created successfully!           ${GREEN}║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
  echo ""

  echo -e "${CYAN}Resources created:${NC}"
  echo "  $CHECK Workspace directory: workspaces/Working_Member/$TEACHER_ID/"
  if [ -n "$CLASS_CODE" ]; then
    echo "  $CHECK Class folder: workspaces/Working_Member/$TEACHER_ID/projects/class-$CLASS_CODE/"
  fi
  echo "  $CHECK Permissions updated: ai-core/acl.yaml"
  echo "  $CHECK Personal branch: $BRANCH_NAME"
  echo ""

  # ── Self-check checklist ──
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${YELLOW}  Self-check (David must verify before notifying teacher)${NC}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
  echo "  [ ] acl.yaml email matches what teacher will put in environment.env"
  echo "      Registered email: $EMAIL"
  echo ""
  echo "  [ ] acl.yaml github_username is correct"
  echo "      Registered username: $GITHUB_USERNAME"
  echo ""
  echo "  [ ] Commit and push this change so teacher can pull"
  echo ""

  echo -e "${CYAN}Send the following to the new teacher:${NC}"
  echo ""
  echo "  - Confirmed email: $EMAIL"
  echo "    (MUST match your setup/environment.env USER_EMAIL)"
  echo "  - Personal branch: $BRANCH_NAME"
  echo "  - Run: bash setup/quick-start.sh"
  echo ""

  print_info "All setup complete. Enjoy teaching, $TEACHER_NAME!"
  echo ""
}

# ============================================================
# Main workflow
# ============================================================

main() {
  print_banner
  check_admin
  collect_teacher_info
  confirm_info
  create_workspace
  update_acl
  create_class_folder
  create_teacher_branch
  print_summary
}

# Execute main workflow
main
