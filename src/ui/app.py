"""
Prompt Forge Studio - Streamlit UI
"""
import streamlit as st
from datetime import datetime
from typing import Optional
import plotly.graph_objects as go

from src.config import config
from src.api.anthropic_client import AnthropicClient
from src.db.database import Database
from src.core.analyzer import PromptAnalyzer
from src.core.tester import PromptTester


# Page configuration
st.set_page_config(
    page_title="Prompt Forge Studio",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = Database()

    if 'api_configured' not in st.session_state:
        st.session_state.api_configured = config.validate()

    if 'current_prompt_id' not in st.session_state:
        st.session_state.current_prompt_id = None

    if 'current_version_id' not in st.session_state:
        st.session_state.current_version_id = None


def get_client() -> Optional[AnthropicClient]:
    """Get configured Anthropic client"""
    try:
        return AnthropicClient()
    except Exception as e:
        st.error(f"Error initializing API client: {str(e)}")
        return None


def render_sidebar():
    """Render sidebar with navigation and prompts list"""
    with st.sidebar:
        st.title("🔨 Prompt Forge Studio")
        st.caption(f"v{config.APP_VERSION}")

        # API Configuration
        with st.expander("⚙️ API Configuration", expanded=not st.session_state.api_configured):
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                value=config.ANTHROPIC_API_KEY or "",
                help="Enter your Anthropic API key"
            )

            if st.button("Save API Key"):
                config.set_api_key(api_key)
                st.session_state.api_configured = config.validate()
                if st.session_state.api_configured:
                    st.success("API key saved!")
                    st.rerun()
                else:
                    st.error("Please enter a valid API key")

        st.divider()

        # Navigation
        page = st.radio(
            "Navigation",
            ["📝 Editor", "📊 Analysis", "🧪 Testing", "📚 Library"],
            label_visibility="collapsed"
        )

        st.divider()

        # Prompts List
        st.subheader("Your Prompts")

        if st.button("➕ New Prompt", use_container_width=True):
            st.session_state.show_new_prompt_dialog = True

        prompts = st.session_state.db.list_prompts()

        if prompts:
            for prompt in prompts:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"{prompt['name']}",
                        key=f"prompt_{prompt['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_prompt_id = prompt['id']
                        version = st.session_state.db.get_current_version(prompt['id'])
                        if version:
                            st.session_state.current_version_id = version['id']
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{prompt['id']}"):
                        st.session_state.db.delete_prompt(prompt['id'])
                        if st.session_state.current_prompt_id == prompt['id']:
                            st.session_state.current_prompt_id = None
                            st.session_state.current_version_id = None
                        st.rerun()
        else:
            st.info("No prompts yet. Create one to get started!")

        return page


def render_new_prompt_dialog():
    """Render dialog for creating new prompt"""
    if st.session_state.get('show_new_prompt_dialog', False):
        with st.form("new_prompt_form"):
            st.subheader("Create New Prompt")

            name = st.text_input("Prompt Name*", placeholder="e.g., Medical Report Analyzer")
            description = st.text_area("Description", placeholder="What does this prompt do?")
            initial_content = st.text_area(
                "Initial Content",
                placeholder="Start writing your prompt here...",
                height=200
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Create", use_container_width=True):
                    if name:
                        prompt_id = st.session_state.db.create_prompt(
                            name=name,
                            description=description,
                            content=initial_content
                        )
                        st.session_state.current_prompt_id = prompt_id
                        version = st.session_state.db.get_current_version(prompt_id)
                        if version:
                            st.session_state.current_version_id = version['id']
                        st.session_state.show_new_prompt_dialog = False
                        st.success(f"Created prompt: {name}")
                        st.rerun()
                    else:
                        st.error("Please enter a prompt name")

            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_new_prompt_dialog = False
                    st.rerun()


def render_editor_page():
    """Render the main editor page"""
    st.title("📝 Prompt Editor")

    if not st.session_state.current_prompt_id:
        st.info("Select a prompt from the sidebar or create a new one to get started.")
        return

    # Get current prompt and version
    prompt = st.session_state.db.get_prompt(st.session_state.current_prompt_id)
    version = st.session_state.db.get_current_version(st.session_state.current_prompt_id)

    if not prompt or not version:
        st.error("Error loading prompt")
        return

    # Header with prompt info
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.subheader(prompt['name'])
        if prompt['description']:
            st.caption(prompt['description'])
    with col2:
        st.metric("Current Version", f"v{version['version']}")
    with col3:
        if st.button("💾 Save New Version", use_container_width=True):
            st.session_state.show_save_version = True

    # Editor
    st.divider()

    prompt_content = st.text_area(
        "System Prompt",
        value=version['content'],
        height=400,
        key="prompt_editor",
        help="Write your system prompt here"
    )

    # Quick actions
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Analyze Quality", use_container_width=True):
            if st.session_state.api_configured:
                st.session_state.show_analysis = True
            else:
                st.error("Please configure your API key first")

    with col2:
        if st.button("🔄 Generate Variants", use_container_width=True):
            if st.session_state.api_configured:
                st.session_state.show_variants = True
            else:
                st.error("Please configure your API key first")

    with col3:
        if st.button("🧪 Run Tests", use_container_width=True):
            if st.session_state.api_configured:
                st.session_state.show_tests = True
            else:
                st.error("Please configure your API key first")

    with col4:
        if st.button("📜 Version History", use_container_width=True):
            st.session_state.show_history = True

    # Save version dialog
    if st.session_state.get('show_save_version', False):
        with st.form("save_version_form"):
            st.subheader("Save New Version")
            notes = st.text_area("Version Notes", placeholder="What changed in this version?")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save", use_container_width=True):
                    version_id = st.session_state.db.create_version(
                        prompt_id=st.session_state.current_prompt_id,
                        content=prompt_content,
                        notes=notes
                    )
                    st.session_state.current_version_id = version_id
                    st.session_state.show_save_version = False
                    st.success("New version saved!")
                    st.rerun()

            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_save_version = False
                    st.rerun()

    # Version history
    if st.session_state.get('show_history', False):
        st.divider()
        st.subheader("Version History")

        versions = st.session_state.db.list_versions(st.session_state.current_prompt_id)

        for v in versions:
            with st.expander(f"Version {v['version']} - {v['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                st.text(v['content'])
                if v['notes']:
                    st.caption(f"Notes: {v['notes']}")

                if st.button(f"Load Version {v['version']}", key=f"load_v{v['id']}"):
                    st.session_state.current_version_id = v['id']
                    st.rerun()

        if st.button("Close History"):
            st.session_state.show_history = False
            st.rerun()


def render_analysis_page():
    """Render the analysis page"""
    st.title("📊 Quality Analysis")

    if not st.session_state.current_prompt_id or not st.session_state.api_configured:
        st.info("Select a prompt and configure your API key to run analysis.")
        return

    version = st.session_state.db.get_current_version(st.session_state.current_prompt_id)
    if not version:
        st.error("No version selected")
        return

    st.subheader(f"Analyzing Version {version['version']}")

    # Analysis options
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Comprehensive", "Clarity", "Completeness", "Efficiency", "Safety"],
        help="Choose the type of analysis to perform"
    )

    if st.button("🔍 Run Analysis", use_container_width=True):
        client = get_client()
        if not client:
            return

        analyzer = PromptAnalyzer(client, st.session_state.db)

        with st.spinner("Analyzing prompt..."):
            if analysis_type == "Comprehensive":
                results = analyzer.analyze_all_dimensions(
                    version['content'],
                    version_id=version['id']
                )

                # Show summary
                summary = analyzer.get_quality_summary(results)

                st.metric("Average Quality Score", f"{summary['average_score']:.1f}/100" if summary['average_score'] else "N/A")

                # Radar chart
                if summary['dimension_scores']:
                    scores = summary['dimension_scores']
                    categories = list(scores.keys())
                    values = list(scores.values())

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name='Scores'
                    ))

                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="Quality Dimensions"
                    )

                    st.plotly_chart(fig, use_container_width=True)

                # Show detailed results
                for result in results:
                    with st.expander(f"{result['type'].title()} Analysis - Score: {result['score'] if result['score'] else 'N/A'}"):
                        st.markdown(result['content'])

            else:
                # Single dimension analysis
                analysis_map = {
                    "Clarity": analyzer.analyze_clarity,
                    "Completeness": analyzer.analyze_completeness,
                    "Efficiency": analyzer.analyze_efficiency,
                    "Safety": analyzer.analyze_safety
                }

                result = analysis_map[analysis_type](version['content'], version_id=version['id'])

                st.metric(f"{analysis_type} Score", f"{result['score']}/100" if result['score'] else "N/A")
                st.markdown(result['content'])

    # Show previous analyses
    st.divider()
    st.subheader("Previous Analyses")

    analyses = st.session_state.db.get_analyses(version['id'])

    if analyses:
        for analysis in analyses:
            with st.expander(f"{analysis['analysis_type'].title()} - {analysis['created_at'].strftime('%Y-%m-%d %H:%M')}"):
                st.metric("Score", f"{analysis['score']}/100" if analysis['score'] else "N/A")
                st.markdown(analysis['content'])
    else:
        st.info("No analyses yet. Run your first analysis above!")


def render_testing_page():
    """Render the testing page"""
    st.title("🧪 Testing")

    if not st.session_state.current_prompt_id or not st.session_state.api_configured:
        st.info("Select a prompt and configure your API key to run tests.")
        return

    version = st.session_state.db.get_current_version(st.session_state.current_prompt_id)
    if not version:
        st.error("No version selected")
        return

    tab1, tab2 = st.tabs(["Test Cases", "Run Tests"])

    with tab1:
        st.subheader("Test Cases")

        # Create new test case
        with st.expander("➕ Create New Test Case"):
            with st.form("new_test_case"):
                name = st.text_input("Test Name", placeholder="e.g., Normal case - complete data")
                input_text = st.text_area("Test Input", placeholder="Input to send to the prompt")
                expected_output = st.text_area("Expected Output (optional)", placeholder="What output do you expect?")
                criteria = st.text_area(
                    "Evaluation Criteria",
                    value="The response should be accurate, well-formatted, and follow the prompt instructions.",
                    placeholder="How should the output be evaluated?"
                )

                if st.form_submit_button("Create Test Case"):
                    if name and input_text and criteria:
                        st.session_state.db.create_test_case(
                            prompt_id=st.session_state.current_prompt_id,
                            name=name,
                            input_text=input_text,
                            expected_output=expected_output if expected_output else None,
                            evaluation_criteria=criteria
                        )
                        st.success(f"Created test case: {name}")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")

        # List existing test cases
        test_cases = st.session_state.db.get_test_cases(st.session_state.current_prompt_id)

        if test_cases:
            for tc in test_cases:
                with st.expander(f"📋 {tc['name']}"):
                    st.text_area("Input", value=tc['input_text'], disabled=True, key=f"input_{tc['id']}")
                    if tc['expected_output']:
                        st.text_area("Expected Output", value=tc['expected_output'], disabled=True, key=f"expected_{tc['id']}")
                    st.text_area("Criteria", value=tc['evaluation_criteria'], disabled=True, key=f"criteria_{tc['id']}")

                    if st.button(f"Delete Test Case", key=f"delete_tc_{tc['id']}"):
                        st.session_state.db.delete_test_case(tc['id'])
                        st.rerun()
        else:
            st.info("No test cases yet. Create one above!")

    with tab2:
        st.subheader("Run Tests")

        test_cases = st.session_state.db.get_test_cases(st.session_state.current_prompt_id)

        if not test_cases:
            st.warning("Create test cases first before running tests.")
            return

        if st.button("▶️ Run All Tests", use_container_width=True):
            client = get_client()
            if not client:
                return

            tester = PromptTester(client, st.session_state.db)

            with st.spinner("Running tests..."):
                results = tester.run_all_tests(
                    prompt_id=st.session_state.current_prompt_id,
                    version_id=version['id'],
                    system_prompt=version['content']
                )

                # Show summary
                summary = tester.get_test_summary(version['id'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tests", summary['total_tests'])
                with col2:
                    st.metric("Passed", summary['passed'])
                with col3:
                    st.metric("Average Score", f"{summary['average_score']:.1f}" if summary['average_score'] else "N/A")

                # Show individual results
                st.divider()
                for result in results:
                    with st.expander(f"📊 {result['test_name']} - Score: {result['score'] if result['score'] else 'N/A'}"):
                        st.subheader("Output")
                        st.text_area("", value=result['output'], disabled=True, key=f"output_{result['test_case_id']}")

                        st.subheader("Evaluation")
                        st.markdown(result['evaluation'])

        # Show previous test results
        st.divider()
        st.subheader("Previous Test Results")

        summary = tester.get_test_summary(version['id'])

        if summary['total_tests'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tests", summary['total_tests'])
            with col2:
                st.metric("Passed", summary['passed'])
            with col3:
                st.metric("Average Score", f"{summary['average_score']:.1f}" if summary['average_score'] else "N/A")
        else:
            st.info("No test results yet. Run tests above!")


def render_library_page():
    """Render the library page"""
    st.title("📚 Prompt Library")

    st.info("Feature coming soon: Reusable prompt components, templates, and shared prompts.")

    # Show all prompts with their stats
    prompts = st.session_state.db.list_prompts()

    if prompts:
        for prompt in prompts:
            with st.expander(f"📄 {prompt['name']}"):
                st.write(f"**Description:** {prompt['description'] or 'No description'}")
                st.write(f"**Versions:** {prompt['current_version']}")
                st.write(f"**Last Updated:** {prompt['updated_at'].strftime('%Y-%m-%d %H:%M')}")

                version = st.session_state.db.get_current_version(prompt['id'])
                if version:
                    st.text_area("Current Content", value=version['content'], disabled=True, key=f"lib_{prompt['id']}")


def main():
    """Main application entry point"""
    init_session_state()

    # Render sidebar and get selected page
    page = render_sidebar()

    # Render new prompt dialog if needed
    render_new_prompt_dialog()

    # Render selected page
    if page == "📝 Editor":
        render_editor_page()
    elif page == "📊 Analysis":
        render_analysis_page()
    elif page == "🧪 Testing":
        render_testing_page()
    elif page == "📚 Library":
        render_library_page()


if __name__ == "__main__":
    main()
