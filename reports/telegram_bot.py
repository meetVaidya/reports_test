import telebot
import pandas as pd

from config import TELEGRAM_TOKEN
from database import setup_agent, load_query_repository
from query_utils import get_most_similar_query, format_result, result_to_dataframe, escape_markdown
from visualization import optimize_for_plotting, create_plot

class SalesDataBot:
    def __init__(self):
        self.bot = telebot.TeleBot(TELEGRAM_TOKEN)
        self.agent_executor, self.db = setup_agent()
        self.query_repo = load_query_repository()
        self._register_handlers()

    def _register_handlers(self):
        @self.bot.message_handler(commands=["start", "help"])
        def greet(message):
            self.bot.reply_to(message, "Hi! Ask me anything about the sales data. I'll provide both text results and visualizations when appropriate.")

        @self.bot.message_handler(func=lambda m: True)
        def handle_query(message):
            user_query = message.text

            # Send "typing" action to let user know the bot is processing
            self.bot.send_chat_action(message.chat.id, 'typing')

            # Process the query
            text_response, result_df, title = self.run_query_on_bigquery(user_query)

            # Send text response
            self.bot.send_message(message.chat.id, text_response, parse_mode="MarkdownV2")

            # If we have data to visualize, create and send a plot
            if not result_df.empty and len(result_df) > 0:
                # Optimize data for plotting if needed
                plot_df, strategy = optimize_for_plotting(result_df, user_query)

                # Create plot
                plot_title = f"Results for: {title}"
                img_data = create_plot(plot_df, plot_title, strategy)

                if img_data:
                    # Send plot as photo
                    self.bot.send_photo(message.chat.id, img_data)

    def run_query_on_bigquery(self, user_query: str):
        try:
            best_match = get_most_similar_query(user_query, self.query_repo, method="cosine")
            sql_template = best_match.get("query")
            description = best_match.get("description", "No description found")

            if sql_template:
                result = self.db.run(sql_template)
                formatted_text = f"🔎 Based on similar intent: {escape_markdown(description)}\n\n🧾 Result:\n{format_result(result)}"

                # Convert result to DataFrame for plotting
                df = result_to_dataframe(result)
                return formatted_text, df, description
            else:
                raise ValueError("No SQL template found")

        except Exception as template_err:
            try:
                result = self.agent_executor.invoke(user_query)
                formatted_text = f"💡 Generated via SQL Agent:\n\n🧾 Result:\n{format_result(result)}"

                # Extract result data from agent output
                if isinstance(result, dict) and "result" in result:
                    result_data = result["result"]
                else:
                    result_data = result

                # Convert result to DataFrame for plotting
                df = result_to_dataframe(result_data)
                return formatted_text, df, user_query
            except Exception as agent_err:
                error_msg = f"❌ Both retrieval and agent failed\n\nTemplate error: {escape_markdown(str(template_err))}\nAgent error: {escape_markdown(str(agent_err))}"
                return error_msg, pd.DataFrame(), ""

    def start(self):
        print(" Bot is running with visualization capabilities...")
        self.bot.infinity_polling()
