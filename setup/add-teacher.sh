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

# Prompt for input with validation
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

# Prompt for optional input with default
get_optional_input() {
  local prompt_msg="$1"
  local default_value="$2"
  local input_value

  echo -ne "${CYAN}${prompt_msg}${NC}"
  if [ -n "$default_value" ]; then
    echo -ne " (default: $default_value)${NC}: "
  else
    echo -ne "${NC}: "
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
  print_info "Please provide the following information about the new teacher"
  echo ""

  TEACHER_NAME=$(get_input "Teacher name (Traditional Chinese)")
  EMAIL=$(get_input "Email (for Git authentication)")
  CLASS_CODE=$(get_input "Class code (example: 4c, 9c)")
  SUBJECT=$(get_input "Primary subject (example: English, Taiwanese)")

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
  echo "  Teacher name: $TEACHER_NAME"
  echo "  Email: $EMAIL"
  echo "  Class code: $CLASS_CODE"
  echo "  Primary subject: $SUBJECT"
  echo "  Teacher ID: $TEACHER_ID"
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

  # teacheros-personal.yaml — 新教師最重要的檔案
  if [ -f "$TEMPLATE_DIR/teacheros-personal.yaml" ]; then
    cp "$TEMPLATE_DIR/teacheros-personal.yaml" "$WORKSPACE_DIR/teacheros-personal.yaml"
    print_success "teacheros-personal.yaml copied (teacher must fill this in)"
  else
    print_warning "teacheros-personal.yaml template not found — teacher must create manually"
  fi

  # philosophy.yaml 已廢除（2026-03-04），個人哲學統一在 teacheros-personal.yaml

  if [ -f "$TEMPLATE_DIR/README.md" ]; then
    cp "$TEMPLATE_DIR/README.md" "$WORKSPACE_DIR/README.md"
    print_success "README.md copied"
  fi

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
  teacher_id: {TEACHER_ID}

teaching:
  class_code: {CLASS_CODE}
  primary_subject: {SUBJECT}

workspace:
  path: workspaces/{TEACHER_ID}/
  created_at: {TIMESTAMP}
  status: active
EOF

  # Replace placeholders
  sed -i.bak "s/{TEACHER_NAME}/$TEACHER_NAME/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{EMAIL}/$EMAIL/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{TEACHER_ID}/$TEACHER_ID/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{CLASS_CODE}/$CLASS_CODE/g" "$WORKSPACE_YAML"
  sed -i.bak "s/{SUBJECT}/$SUBJECT/g" "$WORKSPACE_YAML"
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
      github_username: (TO BE CONFIRMED WITH TEACHER)
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
  echo ""
  print_warning "IMPORTANT: Manually verify and update the github_username field in acl.yaml"
}

# ============================================================
# Create class folder
# ============================================================

create_class_folder() {
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
# Print summary
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
  echo "  ✓ Workspace directory: workspaces/Working_Member/$TEACHER_ID/"
  echo "  ✓ Class folder: workspaces/Working_Member/$TEACHER_ID/projects/class-$CLASS_CODE/"
  echo "  ✓ Permissions updated: ai-core/acl.yaml"
  echo "  ✓ Personal branch: $BRANCH_NAME"
  echo ""

  echo -e "${YELLOW}Next steps (David must complete):${NC}"
  echo ""
  echo "1. Update ai-core/acl.yaml with the teacher's GitHub username:"
  echo "   Find the entry for $TEACHER_NAME and fill in github_username"
  echo ""
  echo "2. Send the following information to the new teacher:"
  echo "   - Teacher ID: $TEACHER_ID"
  echo "   - Class code: $CLASS_CODE"
  echo "   - Confirmed email: $EMAIL"
  echo "   - Personal branch: $BRANCH_NAME"
  echo "   - Instruction to run: bash setup/quick-start.sh"
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
