import argparse
import warnings


def _print_memory_usage():
    try:
        import psutil
    except ModuleNotFoundError:
        return

    used_gb = psutil.virtual_memory().used / 1_000_000_000
    print(f'RAM memory used (GB): {used_gb:.2f}')


def _sample_frames(frames, quick_rows):
    if quick_rows is None:
        return frames
    return tuple(frame.head(quick_rows).copy(deep=True) for frame in frames)


def analysis(
    skip_exploration=False,
    skip_delivery=False,
    skip_review=False,
    skip_network=False,
    quick_rows=None
):
    warnings.simplefilter(action='ignore', category=FutureWarning)

    from src.local import local_access_df

    customers, geolocation, order_items, order_payment, order_reviews, order_dataset, products, sellers, product_category = _sample_frames(
        local_access_df(),
        quick_rows
    )

    if not skip_exploration:
        from analysis.exploration import Exploration

        # Step 1: basic data checks
        for frame in [customers, order_dataset, order_payment, order_reviews]:
            Exploration(frame).df_info_()

    from analysis.commercial import order_customer

    # Step 2: commercial analysis
    orders_customers_items, customer_once, clv = order_customer(
        order_dataset,
        customers,
        order_payment,
        order_items,
        products,
        product_category
    )
    print('Commercial Analysis is Completed')
    print('-' * 20)

    if not skip_delivery:
        from analysis.delivery import delivery_analysis

        delivery_analysis(orders_customers_items, sellers, geolocation)
        _print_memory_usage()

    if not skip_review:
        from analysis.review import review_analysis

        review_analysis(order_reviews)
        _print_memory_usage()

    if not skip_network:
        from analysis.network import network_analysis

        network_analysis(orders_customers_items, sellers)

    return orders_customers_items, customer_once, clv


def _parse_args():
    parser = argparse.ArgumentParser(description='Run the Olist e-commerce analytics pipeline.')
    parser.add_argument('--skip-exploration', action='store_true', help='Skip exploration prints.')
    parser.add_argument('--skip-delivery', action='store_true', help='Skip delivery modeling step.')
    parser.add_argument('--skip-review', action='store_true', help='Skip review NLP step.')
    parser.add_argument('--skip-network', action='store_true', help='Skip network analysis step.')
    parser.add_argument(
        '--quick-rows',
        type=int,
        default=None,
        help='Use only the first N rows from each dataset for a quick smoke run.'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    try:
        analysis(
            skip_exploration=args.skip_exploration,
            skip_delivery=args.skip_delivery,
            skip_review=args.skip_review,
            skip_network=args.skip_network,
            quick_rows=args.quick_rows
        )
    except KeyboardInterrupt:
        print('Interrupted')
    except ModuleNotFoundError as error:
        print(
            f"Missing dependency '{error.name}'. "
            "Install packages from requirements.txt before running this pipeline."
        )
