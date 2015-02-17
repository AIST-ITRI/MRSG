#include <unistd.h>
#include <cmath>
#include <vector>
#include <iostream>
#include <fstream>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>

#include <mrsg.h>
#include <scheduling.h>

using boost::lexical_cast;
using boost::algorithm::trim;

size_t choose_remote_map_task (size_t wid);
void usage(const char* prog) __attribute__((noreturn));

std::vector<double> s_map_cost;
std::vector<double> s_red_cost;
std::vector< std::vector<int> > s_map_output;

void read_cost(const char* filename, std::vector<double>& result)
{
    std::ifstream ifs(filename);

    if (!ifs.is_open()) {
        std::cerr << "Can't open " << filename << "." << std::endl;
        std::exit(1);
    }
    int nline = 1;
    std::string line;
    try {
        while (std::getline(ifs, line)) {
            trim(line);
            double v = lexical_cast<double>(line);
            if (!std::isfinite(v) || v < 0) {
                std::cerr << "[" << filename << ":" << nline << "] " << v << " is invalid." << std::endl;
                std::exit(1);
            }
            result.push_back(v);
            nline++;
        }
    } catch (const boost::bad_lexical_cast& e) {
        std::cerr << "[" << filename << ":" << nline << "] " << "Can't convert to double: " << line << std::endl;
        std::cerr << "[" << filename << ":" << nline << "] " << e.what() << std::endl;
        std::exit(1);
    }
}

void read_map_output(const char* filename, std::vector< std::vector<int> >& result)
{
    std::ifstream ifs(filename);

    if (!ifs.is_open()) {
        std::cerr << "Can't open " << filename << "." << std::endl;
        std::exit(1);
    }
    int nline = 1;
    std::string line;
    try {
        while (std::getline(ifs, line)) {
            std::istringstream ls(line);
            std::string item;

            result.push_back(std::vector<int>());

            while (std::getline(ls, item, ',')) {
                trim(item);
                int v = lexical_cast<int>(item);
                if (v < 0) {
                    std::cerr << "[" << filename << ":" << nline << "] " << v << " is invalid." << std::endl;
                    std::exit(1);
                }
                result.back().push_back(v);
            }
            nline++;
        }
    } catch (const boost::bad_lexical_cast& e) {
        std::cerr << "[" << filename << ":" << nline << "] " << "Can't convert to int: " << line << std::endl;
        std::cerr << "[" << filename << ":" << nline << "] " << e.what() << std::endl;
        std::exit(1);
    }
}

int my_map_output_function(size_t mid, size_t rid)
{
    return s_map_output.at(mid).at(rid);
}

double my_task_cost_function(enum phase_e phase, size_t tid, size_t wid)
{
    switch (phase) {
    case MAP:
        return s_map_cost.at(tid);
    case REDUCE:
        return s_red_cost.at(tid);
    }
}

/**
 * @brief  Chooses a map or reduce task and send it to a worker.
 * @param  phase  MAP or REDUCE.
 * @param  wid  Worker id.
 * @return Chosen task id.
 */
size_t remote_scheduler_f (enum phase_e phase, size_t wid)
{
    switch (phase) {
    case MAP:
        return choose_remote_map_task (wid);

    case REDUCE:
        return choose_default_reduce_task (wid);

    default:
        return NONE;
    }
}

/**
 * @brief  Choose a map task, and send it to a worker.
 * @param  wid  Worker id.
 */
size_t choose_remote_map_task (size_t wid)
{
    size_t           chunk;
    size_t           tid = NONE;
    enum task_type_e task_type, best_task_type = NO_TASK;

    if (job.tasks_pending[MAP] <= 0)
	return tid;

    /* Look for a task for the worker. */
    for (chunk = 0; chunk < config.chunk_count; chunk++)
    {
	task_type = get_task_type (MAP, chunk, wid);

	if (task_type == REMOTE)
	{
	    tid = chunk;
	    break;
	}
	else if (task_type == LOCAL
		|| (job.task_instances[MAP][chunk] < 2 // Speculative
		    && task_type < best_task_type ))   // tasks.
	{
	    best_task_type = task_type;
	    tid = chunk;
	}
    }

    return tid;
}

void usage(const char* prog)
{
    std::cerr << "Usage: " << prog << "[-r] platform_xml deploy_xml mrsg_conf map_cost red_cost map_output" << std::endl;
    std::exit(1);
}

int main(int argc, char* argv[])
{
    const char* platform   = "";
    const char* deploy     = "";
    const char* conf       = "";
    const char* map_cost   = "";
    const char* red_cost   = "";
    const char* map_output = "";
    int opt;
    bool use_remote_scheduler = false;
    int index;
    int exitcode = 1;

    while ((opt = getopt(argc, argv, "r")) != -1) {
        switch (opt) {
        case 'r':
            use_remote_scheduler = true;
            break;
        default: /* '?' */
            usage(argv[0]);
        }
    }

    if (argc != optind + 6) {
        std::cerr << "mismatch number of arguments. " << argv[0] << " requires 6 arguments." << std::endl;
        usage(argv[0]);
    }

    index = optind;
    platform   = argv[index++];
    deploy     = argv[index++];
    conf       = argv[index++];
    map_cost   = argv[index++];
    red_cost   = argv[index++];
    map_output = argv[index++];

    read_cost(map_cost, s_map_cost);
    read_cost(red_cost, s_red_cost);
    read_map_output(map_output, s_map_output);

    std::cerr << "platform:   " << platform << std::endl;
    std::cerr << "deploy:     " << deploy << std::endl;
    std::cerr << "conf:       " << conf << std::endl;
    std::cerr << "map_cost:   " << map_cost << std::endl;
    std::cerr << "red_cost:   " << red_cost << std::endl;
    std::cerr << "red_output: " << map_output<< std::endl;

    MRSG_init();
    MRSG_set_task_cost_f(my_task_cost_function);
    MRSG_set_map_output_f(my_map_output_function);
    if (use_remote_scheduler) {
        MRSG_set_scheduler_f(remote_scheduler_f);
    }
    MRSG_main(platform, deploy, conf);

    return 0;
}
